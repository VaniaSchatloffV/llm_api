import os

import json
import numpy as np
import pandas as pd

from botocore.exceptions import ClientError
import tiktoken

from configs.config import get_settings
from handlers.DBORMHandler import DB_ORM_Handler
from helpers import conversation_helper, file_helper, llm_helper

settings = get_settings()

retry = 3
URL = settings.host + ":" + str(settings.port)

def send_prompt(question, messages: list):
    response = llm_helper.invoke_llm(question=question, messages=messages)
    return response

def execute_query(query):
    try:
        with DB_ORM_Handler() as db:
            data = db.query(query, return_data=True)
            return {"data": data, "error": None}
    except Exception as e:
        return {"data": None, "error": str(e)}

def send_prompt_and_process(prompt: str, conversation_id: int, user_id: int):
    # si no existe la conversación, se crea y retorna nuevo id

    if conversation_id == 0:
        conversation_id = conversation_helper.new_conversation(user_id)

    response_format = {
        "response" : None,
        "conversation_id" : conversation_id
    }

    last_option_message = conversation_helper.get_option_messages(conversation_id)
    if prompt in file_helper.OPTIONS and last_option_message and last_option_message.get("role") == "assistant":
        conversation_helper.insert_message(conversation_id, "user", prompt, "option")
        query = conversation_helper.get_last_query(conversation_id)
        with DB_ORM_Handler() as db:
            data = db.query(query, return_data=True)
        file_id = file_helper.to_file(prompt, data)
        resp = {"text": "El archivo ya está listo", "file_id": file_id, "file_type": prompt}
        conversation_helper.insert_message(conversation_id, "assistant", resp, "file")
        return {"response": resp, "conversation_id": conversation_id}
    else:
        conversation_helper.insert_message(conversation_id, "user", prompt)
    
    # Se obtienen mensajes anteriores para la llm
    messages = conversation_helper.get_messages_for_llm(conversation_id)
    messages_for_llm = llm_helper.format_llm_memory(messages)

    print("pasó format llm memory linea 57", "\n")

    classifier = llm_helper.LLM_Identify_NL(prompt, messages)

    print("pasó llm identify", classifier, "\n")

    if classifier != "SQL":
        conversation_helper.insert_message(conversation_id, "assistant", classifier)
        response_format["response"] = {"text": classifier}
        print("Era SQL", response_format, "\n")
        return response_format
    

    resp = send_prompt(prompt , messages_for_llm)
    print("send_prompt", resp, "\n")
    # Verificacion del mensaje
    verification = llm_helper.LLM_recognize_SQL(resp.get("answer"))
    print("verification", verification, "\n")
    if verification == "NL":
        conversation_helper.insert_message(conversation_id, "assistant", resp.get("answer"))
        print("verification es NL, mensaje insertado, returned", str({"response": resp.get("answer"), "conversation_id": conversation_id}), "\n")
        return {"response": resp.get("answer"), "conversation_id": conversation_id}
    elif verification == "SQL":
        # Ejecución de la consulta
        print("Era SQL", "\n")
        query = resp.get("answer")
        conversation_helper.insert_message(conversation_id, "assistant", query, "query")
        print("mensaje insertado linea 85", "\n")
        db_response = execute_query(query)
        print("db_response", db_response, "\n")
        
        if db_response.get("error") is not None:
            success = False
            for i in range(retry):
                error = db_response.get("error")
                query = llm_helper.LLM_Fix_SQL(prompt, query, error)
                conversation_helper.insert_message(conversation_id, "assistant", query, "query_review")
                db_response = execute_query(query)
                if db_response.get("error") is None:
                    success = True
                    break
            if not success:
                response_format["response"] = {"text": "Ha ocurrido un error con su consulta, por favor contacte a administración de la plataforma para solucionarlo."}
                return response_format

        data = db_response.get("data")

        # PARA REVISAR EL NUMERO DE TOKENS DE LA RESPUESTA
        encoding = tiktoken.encoding_for_model("gpt-3.5")
        tokens_used = encoding.encode(str(data))

        option_msg = "¿En qué formato desea recibir la información?"

        if len(tokens_used) < 500: #REVISAR cantidad Y VER SI LO LIMPIAMOS
            nl_complete_response = llm_helper.LLM_Translate_Data_to_NL(data, prompt, query) + " " + option_msg 
            response_format["response"] = {"text": nl_complete_response, "options": file_helper.OPTIONS}
            conversation_helper.insert_message(conversation_id, "assistant", response_format.get("response"), "option")
            
        else:
            response_format["response"] = {"text": option_msg, "options": file_helper.OPTIONS}
            conversation_helper.insert_message(conversation_id, "assistant", response_format.get("response"), "option")
        
        return response_format