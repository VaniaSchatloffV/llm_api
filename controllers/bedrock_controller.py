import os
import boto3
import json
import numpy as np
import pandas as pd

from botocore.exceptions import ClientError

from configs.config import get_settings
from handlers.DBORMHandler import DB_ORM_Handler
from helpers import conversation_helper, file_helper

settings = get_settings()

URL = settings.host + ":" + str(settings.port)

def invoke_llm(messages: list, system_prompt: str, temperature=0.1, top_p=0.9):
    """
    Invokes Anthropic Claude 3 Sonnet to run an inference using the input
    provided in the request body.

    :param prompt: The prompt that you want Claude 3 to complete.
    :return: Inference response from the model.
    """
    # Initialize the Amazon Bedrock runtime client
    client = boto3.client(
        service_name="bedrock-runtime", region_name="us-east-1"
    )
    # Invoke Claude 3 with the text prompt
    model_id = "anthropic.claude-v2:1"
    body = json.dumps(
                {
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": 1024,
                    "temperature": temperature,
                    "top_p": top_p,
                    "system": system_prompt,
                    "messages": messages
                }
    )
    try:
        response = client.invoke_model(
            modelId=model_id,
            body=body
        )
        # Process and print the response
        result = json.loads(response.get("body").read())
        input_tokens = result["usage"]["input_tokens"]
        output_tokens = result["usage"]["output_tokens"]
        output_list = result.get("content", [])
        return output_list

    except ClientError as err:
        print(
            "Couldn't invoke Claude 3 Sonnet. Here's why: %s: %s",
            err.response["Error"]["Code"],
            err.response["Error"]["Message"],
        )
        raise err


def send_prompt(messages: list):
    system_prompt = """ Las siguientes son descripciones de una tabla y sus campos en una base de datos:

                create table messages(
                    id SERIAL,
                    conversation_id INT,
                    message JSON,
                    created_at TIMESTAMP default NOW(),
                    PRIMARY KEY(id),
                    FOREIGN KEY (conversation_id) REFERENCES conversations(id));

                create table conversations(
                    id SERIAL,
                    user_id INT,
                    name varchar(256),
                    created_at TIMESTAMP default NOW(),
                    finished_at TIMESTAMP,
                    PRIMARY KEY (id));
                
                CREATE TABLE users (
                    id SERIAL,
                    name VARCHAR(128),
                    lastname VARCHAR(128),
                    email VARCHAR(256),
                    password VARCHAR(512),
                    role_id INT,
                    PRIMARY KEY (id)
                );

                Con esta información, necesito que traduzcas consultas en lenguaje natural a consultas SQL.

                No respondas con nada más que el SQL generado, un ejemplo de esto es: "SELECT * FROM pacientes;", fijate como NO hay '\n' en la respuesta. Tampoco agregues cordialidades o explicaciones, responde solo con SQL.

                Si se te pide información que no esta en la tabla no la agregues a la consulta, responde lo que puedas, pero no des explicaciones, responde solo con SQL.

                Si se te pide modificar la base de datos, indica que no lo tienes permitido, este es el unico caso donde puedes no usar SQL.""" 
    response =  invoke_llm(messages=messages, system_prompt=system_prompt)
    return response

    

def send_prompt_and_process(prompt: str, conversation_id: int, user_id: int):
    # si no existe la conversación, se crea y retorna nuevo id
    if conversation_id == 0:
        conversation_id = conversation_helper.new_conversation(user_id)

    # Si el prompt es un tipo de archivo
    if prompt in file_helper.OPTIONS:
        # se revisa si el ultimo mensaje fue pidiendo el tipo de archivo
        last_message = conversation_helper.get_option_messages(conversation_id)
        if last_message and last_message.get("role") == "assistant":
            conversation_helper.insert_message(conversation_id, "user", prompt, "option")
        else:
            conversation_helper.insert_message(conversation_id, "user", prompt)
    else:
        conversation_helper.insert_message(conversation_id, "user", prompt)
    
    # Se obtienen mensajes anteriores para la llm
    messages = conversation_helper.get_messages_for_llm(conversation_id)

    # Si el mensaje es para definir el archivo de descarga
    if prompt in file_helper.OPTIONS:
        print(prompt)
        try:
            if last_message.get("role") == "assistant":
                query = conversation_helper.get_last_query(conversation_id)
                print(query)
                with DB_ORM_Handler() as db:
                    data = db.query(query, return_data=True)
                file_id = file_helper.to_file(prompt, data)
                resp = {"text": "El archivo ya está listo", "file_id": file_id, "file_type": prompt}
                conversation_helper.insert_message(conversation_id, "assistant", resp, type="file")
                return {"response": resp, "conversation_id": conversation_id}
        except Exception as e:
            print(e)
            pass
    response = send_prompt(messages)
    resp = response[0].get("text")
    if "SELECT" in resp:
        query = resp
        query = query.split("SELECT")[1]
        query = "SELECT " + query.split(";")[0]
        conversation_helper.insert_message(conversation_id, "assistant", query, "query")
        resp = {"text": "¿En qué formato desea recibir la información?"}
        resp["options"] = file_helper.OPTIONS
        conversation_helper.insert_message(conversation_id, "assistant", resp, type="option")
        return {"response": resp, "conversation_id": conversation_id}

    conversation_helper.insert_message(conversation_id, "assistant", resp)
    return {"response": resp, "conversation_id": conversation_id}