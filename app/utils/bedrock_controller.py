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

def file_to_dataframe(file):
    file = file.pop()
    file = file.get_dictionary()
    file_path = file_helper.get_file_path(file.get("id"))
    if file.get("extension") == "csv":
        return pd.read_csv(file_path), file_path
    if file.get("extension") == "xlsx":
        return pd.read_excel(file_path), file_path


def send_prompt_and_process(user_message: str, conversation_id: int, user_id: int):
    # si no existe la conversación, se crea y retorna nuevo id

    if conversation_id == 0:
        conversation_id = conversation_helper.new_conversation(user_id)

    response_format = {
        "response" : None,
        "conversation_id" : conversation_id
    }

    # Se obtienen mensajes anteriores para la llm
    messages = conversation_helper.get_messages(conversation_id)
    messages_for_llm = llm_helper.format_llm_memory(messages)
    classifier = llm_helper.LLM_Identify_NL(user_message, messages_for_llm)

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

    #Ruta para cuando el identify reconoce una conversacion
    if classifier != "SQL" and not(classifier in file_helper.OPTIONS) and classifier != "graph":
        conversation_helper.insert_message(conversation_id, "user", user_message)
        conversation_helper.insert_message(conversation_id, "assistant", classifier)
        response_format["response"] = {"text": classifier}
        return response_format
    
    #Ruta para cuando el identify reconoce como grafico
    if classifier == "graph":
        conversation_helper.insert_message(conversation_id, "user", user_message, "conversation")
        file = file_helper.get_last_file_from_conversation(conversation_id=conversation_id)
        if file: 
            df_d, file_path = file_to_dataframe(file)
            graph_option = llm_helper.LLM_graphgen(df_d.columns,user_message, messages_for_llm)
            dic_go = json.loads(graph_option)
            if dic_go.get("faltan_datos") == "false":
                return generate_and_response_graph(file_path, dic_go, user_id, conversation_id, response_format)
            if dic_go.get("faltan_datos") == "true":
                #LOGICA DE FLUJO ORIGINAL PERO CON LLM_SQL_GRAPH
                conversation_helper.insert_message(conversation_id, "assistant", dic_go, "missing_info")
                messages = conversation_helper.get_messages_for_llm(conversation_id)
                messages_for_llm = llm_helper.format_llm_memory(messages)
                data, query = generate_query_and_data(user_message, conversation_id, user_id, response_format, messages_for_llm, messages)        
                file = file_helper.get_last_file_from_conversation(conversation_id=conversation_id)
                if file: 
                    df_d, file_path = file_to_dataframe(file)
                    graph_option = llm_helper.LLM_graphgen(df_d.columns,user_message, messages_for_llm)
                    dic_go = json.loads(graph_option)
                    return generate_and_response_graph(file_path, dic_go, user_id, conversation_id, response_format)
        return {"response": "No tengo informacion con la que pueda realizar un grafico, haz una pregunta referente a la base de datos de FALP.", "conversation_id": conversation_id}
    else:
        messages = conversation_helper.get_messages_for_llm(conversation_id)
        messages_for_llm = llm_helper.format_llm_memory(messages)
        conversation_helper.insert_message(conversation_id, "user", user_message)
        data, query = generate_query_and_data(user_message, conversation_id, user_id, response_format, messages_for_llm, messages)

        # PARA REVISAR EL NUMERO DE TOKENS DE LA RESPUESTA
        encoding = tiktoken.encoding_for_model("gpt-4o")
        tokens_used = encoding.encode(str(data))
        nl_response = llm_helper.LLM_Translate_Data_to_NL(data, user_message, query, tokens_used)
        response_format["response"] = {"text": nl_response}
        conversation_helper.insert_message(conversation_id, "assistant", nl_response, "response")
                    
        return response_format


def generate_query_and_data(user_message, conversation_id, user_id, response_format, messages_for_llm, messages):
    resp = llm_helper.LLM_SQL(question=user_message, messages=messages_for_llm)
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
                # Se actualiza memoria
                messages = conversation_helper.get_messages_for_llm(conversation_id)
                messages_for_llm = llm_helper.format_llm_memory(messages)
                query = llm_helper.LLM_Fix_SQL(user_message, query, error, messages_for_llm)
                verification = llm_helper.LLM_recognize_SQL(query.get("answer"))
                if verification == "SQL":
                    db_response = execute_query(query.get("answer"), user_id, conversation_id)
                    conversation_helper.insert_message(conversation_id, "assistant", {"query": query.get("answer"), "file_id": db_response.get("file_id")}, "query_review")
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
        return data, query


def generate_and_response_graph(file_path, dic_go, user_id, conversation_id, response_format):
    grafico, graph_name = graphic_helper.generar_grafico(file_path,dic_go)
    file_graph_id = file_helper.new_file(user_id, conversation_id, graph_name, "png")
    file_created_msg = {"text": "Tu archivo ya esta listo, indica si requieres algun cambio en tu grafico para volver a generarlo", "graphical_option": dic_go, "file_id": file_graph_id,  "file_type": "png"}
    conversation_helper.insert_message(conversation_id, "assistant", file_created_msg, "file")
    response_format["response"] = {"text": file_created_msg.get("text"), "file_id": file_graph_id, "file_type": "png"}
    return response_format