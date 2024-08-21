import os
import boto3
import json
import numpy as np
import pandas as pd

from botocore.exceptions import ClientError
from handlers.DBHandler import DBHandler
from helpers import conversation_helper, file_helper
from configs.config import get_settings

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


def send_prompt(prompt: str, conversation_id: int, user_id: int):
    if conversation_id == 0:
        conversation_id = conversation_helper.new_conversation(user_id)  # si no existe la conversación, se crea y retorna nuevo id
    conversation_helper.insert_message(conversation_id, "user", prompt)
    messages = conversation_helper.get_messages(conversation_id)
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

    response = invoke_llm(messages=messages, system_prompt=system_prompt)
    
    if "SELECT" in response[0]["text"]:
        query = response[0]["text"]
        query = query.split("SELECT")[1]
        query = "SELECT " + query.split(";")[0]
        with DBHandler() as db:
            data = db.select(query)
            file_name_excel = str(file_helper.to_excel(data))
            file_name_csv = str(file_helper.to_csv(data))
            response = [{"text": "Descargar el archivo en el siguiente link: \nExcel: {} \nCSV: {}".format(URL + "/download/" + file_name_excel + "/xlsx", URL + "/download/" + file_name_csv + "/csv")}]
    else:
        conversation_helper.insert_message(conversation_id, "assistant", response)
    # retorna estructura para leer desde backend-frontend
    return {"response": response[0]["text"], "conversation_id": conversation_id}
