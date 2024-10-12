from botocore.exceptions import ClientError
import tiktoken

from app.dependencies import get_settings
from app.crud.DBORMHandler import DB_ORM_Handler
from .helpers import conversation_helper, file_helper, llm_helper

settings = get_settings()

retry = 3

def execute_query(query, user_id, conversation_id):
    #print("HOLA BUENAS TARDES")
    print(query,user_id,conversation_id)
    try:
        with DB_ORM_Handler() as db:
            data = db.query(query, return_data=True)
            file_name = file_helper.to_file("csv", data)
            file_id = file_helper.new_file(user_id, conversation_id, file_name, "csv")
            return {"data": data, "error": None, "file_id": file_id}
    except Exception as e:
        #print("HA OCURRIDO UN ERROR QUE NO MUESTRO: ", e)
        #print("RETURN: ", {"data": None, "error": str(e), "file_id": -1})
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
    print("MFL:", messages_for_llm)
    classifier = llm_helper.LLM_Identify_NL(user_message, messages_for_llm)
    print("CLASIFICADO COMO: ", classifier)

    if classifier != "SQL" and not(classifier in file_helper.OPTIONS):
        conversation_helper.insert_message(conversation_id, "user", user_message)
        conversation_helper.insert_message(conversation_id, "assistant", classifier)
        response_format["response"] = {"text": classifier}
        return response_format

    if classifier in file_helper.OPTIONS:
        conversation_helper.insert_message(conversation_id, "user", user_message, "option")
        last_query = conversation_helper.get_last_query(conversation_id)
        if last_query:
            print(last_query)
            #print(type(last_query))
            
            csv_file_id = last_query.get("file_id")
            if classifier == "csv":
                print("ARMANDO UN CSV")
                resp = {"text": "El archivo ya está listo", "file_id": csv_file_id, "file_type": classifier}
            elif classifier == "xlsx":
                print("ARMANDO UN XLSX")
                xlsx_file_id = file_helper.csv_to_excel(user_id = user_id, conversation_id = conversation_id, file_id_csv = csv_file_id)
                resp = {"text": "El archivo ya está listo", "file_id": xlsx_file_id, "file_type": classifier}
            conversation_helper.insert_message(conversation_id, "assistant", resp, "file")
            return {"response": resp, "conversation_id": conversation_id}
        else:
            return {"response": "No hay información que retornar, haz una pregunta.", "conversation_id": conversation_id}
    else:
        conversation_helper.insert_message(conversation_id, "user", user_message)
        resp = llm_helper.LLM_SQL(question=user_message, messages=messages_for_llm)
        print(resp)
        # Verificacion del mensaje
        verification = llm_helper.LLM_recognize_SQL(resp.get("answer"))
        #print("Verificador: ", verification)
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
                    print("error:", i, error)
                    messages = conversation_helper.get_messages_for_llm(conversation_id)
                    messages_for_llm = llm_helper.format_llm_memory(messages)
                    query = llm_helper.LLM_Fix_SQL(user_message, query, error, messages_for_llm)
                    
                    
                    
                    verification = llm_helper.LLM_recognize_SQL(query.get("answer"))
                    print(verification)
                    if verification == "SQL":
                        #Revisar
                        db_response = execute_query(query.get("answer"), user_id, conversation_id)
                        print("entre al segundo execute")
                        conversation_helper.insert_message(conversation_id, "assistant", {"query": query.get("answer"), "file_id": db_response.get("file_id")}, "query_review")
                        if db_response.get("error") is None:
                            success = True
                            break
                    else:
                        print("como no entre a SQL, significa que soy NL")
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