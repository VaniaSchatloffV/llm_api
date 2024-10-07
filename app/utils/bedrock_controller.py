from botocore.exceptions import ClientError
import tiktoken
import pandas as pd 
import json

from app.dependencies import get_settings
from app.crud.DBORMHandler import DB_ORM_Handler
from .helpers import conversation_helper, file_helper, llm_helper, graphic_helper

settings = get_settings()

retry = 3

def execute_query(query, user_id, conversation_id):
    try:
        with DB_ORM_Handler() as db:
            data = db.query(query, return_data=True)
            file_name = file_helper.to_file("csv", data)
            file_id = file_helper.new_file(user_id, conversation_id, file_name, "csv")
            return {"data": data, "error": None, "file_id": file_id}
    except Exception as e:
        return {"data": None, "error": str(e), "file_id": -1}

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
    #Ruta para cuando el identify reconoce una conversacion
    if classifier != "SQL" and not(classifier in file_helper.OPTIONS) and classifier != "graph":
        conversation_helper.insert_message(conversation_id, "user", user_message)
        conversation_helper.insert_message(conversation_id, "assistant", classifier)
        response_format["response"] = {"text": classifier}
        return response_format
    
    #Ruta para cuando el identify reconoce como grafico
    if classifier == "graph":
        print("entre a graph")
        conversation_helper.insert_message(conversation_id, "user", user_message, "conversation")
        file = file_helper.get_last_file_from_conversation(conversation_id=conversation_id)
        print(file)
        if file != None: 
            print("holis")
            file = file.pop()
            file = file.get_dictionary()
            file_path = file_helper.get_file_path(file.get("id"))
            if file.get("extension") == "csv":
                df_d = pd.read_csv(file_path)
            if file.get("extension") == "xlsx":
                df_d = pd.read_excel(file_path)


            graph_option = llm_helper.LLM_graphgen(df_d.columns,user_message)
            dic_go = json.loads(graph_option)
            grafico = graphic_helper.generar_grafico(file_path,dic_go['tipo_grafico'],dic_go['x_col'],dic_go['y_col'])
            print(type(grafico))
            file_helper.to_png(grafico)
            conversation_helper.insert_message(conversation_id, "assistant", grafico, "conversation")
            return grafico
        else:
            print("pena")

        

        
    #Ruta para cuando el identify reconoce un mensaje de tipo opcion (csv,xlsx)
    if classifier in file_helper.OPTIONS:
        conversation_helper.insert_message(conversation_id, "user", user_message, "option")
        last_query = conversation_helper.get_last_query(conversation_id)
        if last_query:
            csv_file_id = last_query.get("file_id")
            if classifier == "csv":
                resp = {"text": "El archivo ya está listo", "file_id": csv_file_id, "file_type": classifier}
            elif classifier == "xlsx":
                xlsx_file_id = file_helper.csv_to_excel(user_id = user_id, conversation_id = conversation_id, file_id_csv = csv_file_id)
                resp = {"text": "El archivo ya está listo", "file_id": xlsx_file_id, "file_type": classifier}
            conversation_helper.insert_message(conversation_id, "assistant", resp, "file")
            return {"response": resp, "conversation_id": conversation_id}
        else:
            return {"response": "No hay información que retornar, haz una pregunta.", "conversation_id": conversation_id}
    else:
        conversation_helper.insert_message(conversation_id, "user", user_message)
        resp = llm_helper.LLM_SQL(question=user_message, messages=messages)
        # Verificacion del mensaje
        verification = llm_helper.LLM_recognize_SQL(resp.get("answer"))
        if verification == "NL":
            conversation_helper.insert_message(conversation_id, "assistant", resp.get("answer"))
            return {"response": resp.get("answer"), "conversation_id": conversation_id}
        elif verification == "SQL":
            # Ejecución de la consulta
            query = resp.get("answer")
            db_response = execute_query(query, user_id, conversation_id)
            conversation_helper.insert_message(conversation_id, "assistant", {"query": query, "file_id": db_response.get("file_id")}, "query")
            if db_response.get("error") is not None:
                success = False
                for i in range(retry):
                    error = db_response.get("error")
                    query = llm_helper.LLM_Fix_SQL(user_message, query, error)
                    
                    verification = llm_helper.LLM_recognize_SQL(query.get("answer"))
                    if verification == "SQL":
                        conversation_helper.insert_message(conversation_id, "assistant", query.get("answer"), "query_review")
                        db_response = execute_query(query.get("answer"), user_id, conversation_id)
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
            nl_response = llm_helper.LLM_Translate_Data_to_NL(data, user_message, query, tokens_used)
            response_format["response"] = {"text": nl_response}
            conversation_helper.insert_message(conversation_id, "assistant", response_format.get("response"), "response")
                        
            return response_format