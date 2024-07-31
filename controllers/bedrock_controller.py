import boto3
import json
import numpy as np
import pandas as pd

from botocore.exceptions import ClientError
from helpers import conversation_helper


def invoke_llm(messages: list, system_prompt: str, temperature=0.1, top_p=0.1):
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
    model_id = "anthropic.claude-3-sonnet-20240229-v1:0"
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
    
    #systemPrompt = """Eres un traductor de lenguaje natural a consultas SQL, no respondas con más que la consulta generada, siempre y cuando te den informacion suficiente para hacer una consulta, caso contrario necesito que digas que 
    #necesitas más informacion para poder formular una consulta. No puedes generar consultas que alteren la base de datos, solo SELECTS.
    #Los nombres se guardan en 'nombres', los apellidos en 'sur', el tipo de cancer en 'tipo_cancer', y finalmente clasificacion del cancer en 'categoria_cancer', y la llave primaria es la 'id'. Todo esto 
    #se encuentra en la tabla que se llama pacientes. Estas son las unicas columnas que existen en las tablas, si te dan informacion que no se te entrega, no la coloques en la consulta."""


    #Context
    #reference text
    #instrucciones/describir la estructura de la salida
    
    systemPrompt = """
    Las siguientes son descripciones de una tabla y sus campos en una base de datos:

    Una de las tablas a utilizar es pacientes, esta almacena pacientes cuyos nombres se guardan en el campo 'nombre', sus apellidos en 'sur', la zona que afecta el cáncer 
    en 'tipo_cancer', y la severidad del cancer es un numero del 1 al 5 almacenado en el campo 'categoria_cancer'. Además, la primary key de la tabla es el campo 'id'.
    Otra tabla a usar es doctores, esta almacena información de doctores de FALP, cuyor nombres se guardan en el campo 'nombre', sus apellidos en 'sur', su especialización 
    en 'especialización', y el hospital donde trabaja en 'hospital'. Además, la primary key de la tabla es el campo 'id'.
    Estas dos tablas tienen una tabla intermedia, llamada 'atenciones', esta muestra los pacientes que son tratados por cada doctor con relación varios a varios. Sus campos
    son 'id_atencion', 'id_doctor', tomada desde la tabla 'doctores', y 'id_paciente', tomada desde la tabla 'pacientes'.

    Con esta información, necesito que traduzcas consultas en lenguaje natural a consultas SQL.
    No respondas con nada más que el SQL generado, un ejemplo de esto es: "SELECT * FROM pacientes;", fijate como NO hay '\n' en la respuesta. Tampoco agregues cordialidades o explicaciones, responde solo con SQL.
    Si se te pide informacion que no esta en la tabla no la agregues a la consulta, responde lo que puedas, pero no des explicaciones, responde solo con SQL.
    Si se te pide modificar la base de datos, indica que no lo tienes permitido, este es el unico caso donde puedes no usar SQL.

    """

    response = invoke_llm(messages=messages, system_prompt=systemPrompt)
    # invoca llm
    conversation_helper.insert_message(conversation_id, "assistant", response)
    # retorna estructura para leer desde backend-frontend
    return {"response": response[0]["text"], "conversation_id": conversation_id}
