import os

import json
import numpy as np
import pandas as pd

from botocore.exceptions import ClientError
import tiktoken

from app.dependencies import get_settings
from app.crud.DBORMHandler import DB_ORM_Handler
from .helpers import conversation_helper, file_helper, llm_helper

settings = get_settings()

retry = 3

def execute_query(query):
    try:
        with DB_ORM_Handler() as db:
            data = db.query(query, return_data=True)
            return {"data": data, "error": None}
    except Exception as e:
        return {"data": None, "error": str(e)}

def send_prompt_and_process(user_message: str, conversation_id: int, user_id: int):
    # si no existe la conversación, se crea y retorna nuevo id

    if conversation_id == 0:
        conversation_id = conversation_helper.new_conversation(user_id)

    response_format = {
        "response" : None,
        "conversation_id" : conversation_id
    }

    # Se obtienen mensajes anteriores para la llm
    messages = conversation_helper.get_messages_for_llm(conversation_id)
    messages_for_llm = llm_helper.format_llm_memory(messages)

    classifier = llm_helper.LLM_Identify_NL(user_message, messages_for_llm)
    
    if classifier in file_helper.OPTIONS:
        conversation_helper.insert_message(conversation_id, "user", user_message, "option")
        query = conversation_helper.get_last_query(conversation_id)
        with DB_ORM_Handler() as db:
            data = db.query(query, return_data=True)
        file_name = file_helper.to_file(classifier, data)
        file_id = file_helper.new_file(user_id, conversation_id, file_name, classifier)
        resp = {"text": "El archivo ya está listo", "file_id": file_id, "file_type": classifier}
        conversation_helper.insert_message(conversation_id, "assistant", resp, "file")
        return {"response": resp, "conversation_id": conversation_id}
    else:
        conversation_helper.insert_message(conversation_id, "user", user_message)
    


    if classifier != "SQL":
        conversation_helper.insert_message(conversation_id, "assistant", classifier)
        response_format["response"] = {"text": classifier}
        return response_format
     
    resp = llm_helper.invoke_llm(question=user_message, messages=messages) #DESCOMENTAR ESTO POR FAVOR
    # Verificacion del mensaje
    verification = llm_helper.LLM_recognize_SQL(resp.get("answer"))
    if verification == "NL":
        conversation_helper.insert_message(conversation_id, "assistant", resp.get("answer"))
        return {"response": resp.get("answer"), "conversation_id": conversation_id}
    elif verification == "SQL":
        # Ejecución de la consulta
        query = resp.get("answer")
        conversation_helper.insert_message(conversation_id, "assistant", query, "query")
        db_response = execute_query(query)
        if db_response.get("error") is not None:
            success = False
            for i in range(retry):
                error = db_response.get("error")
                query = llm_helper.LLM_Fix_SQL(user_message, query, error)
                
                verification = llm_helper.LLM_recognize_SQL(query.get("answer"))
                if verification == "SQL":
                    conversation_helper.insert_message(conversation_id, "assistant", query.get("answer"), "query_review")
                    db_response = execute_query(query.get("answer"))
                    if db_response.get("error") is None:
                        success = True
                        break
                else:
                    conversation_helper.insert_message(conversation_id, "assistant", query.get("answer"), "conversation")
                    response_format["response"] = {"text": query.get("answer")}
                    return response_format 
                
            if not success:
                failure_msg = "Ha ocurrido un error con su consulta, por favor contacte a administración de la plataforma para solucionarlo."
                conversation_helper.insert_message(conversation_id, "assistant", failure_msg, "conversation")
                response_format["response"] = {"text": failure_msg}
                return response_format

        data = db_response.get("data")

        # PARA REVISAR EL NUMERO DE TOKENS DE LA RESPUESTA
        encoding = tiktoken.encoding_for_model("gpt-4o")
        tokens_used = encoding.encode(str(data))

        option_msg = "¿En qué formato desea recibir la información?"

        if len(tokens_used) < 500:
            nl_complete_response = llm_helper.LLM_Translate_Data_to_NL(data, user_message, query) + " " + option_msg
            response_format["response"] = {"text": nl_complete_response, "options": file_helper.OPTIONS}
            conversation_helper.insert_message(conversation_id, "assistant", response_format.get("response"), "option")
            
        else:
            response_format["response"] = {"text": option_msg, "options": file_helper.OPTIONS}
            conversation_helper.insert_message(conversation_id, "assistant", response_format.get("response"), "option")
        
        return response_format