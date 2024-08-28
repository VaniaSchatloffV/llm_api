import os
import boto3
import json
import numpy as np
import pandas as pd

from langchain_community.llms import Bedrock
Rafrom langchain_core.prompts import ChatPromptTemplate
from langchain_community.embeddings import BedrockEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain
from langchain.chains import LLMChain


from botocore.exceptions import ClientError
from handlers.DBHandler import DBHandler
from helpers import conversation_helper, file_helper
from configs.config import get_settings

settings = get_settings()

URL = settings.host + ":" + str(settings.port)

#RAG
my_data = [
    """
    En la tabla de nombre: "pacientes"
    se almacena información referente a personas que padecen diferentes tipos de cáncer atendidas por la Fundación oncológica Arturo López Pérez.
    La información almacenada comprende las columnas:
    'id' de tipo int: esta es la clave primaria de la tabla.
    'nombre' de tipo varchar: este campo corresponde al nombre del paciente. Algunos ejemplos de entradas son: 'Juan', 'Ana', 'Pablo', 'Laura', todos parten con mayuscula.
    'sur' de tipo varchar: este campo  corresponde al apellido del paciente. Algunos ejemplos de entradas son: 'Perez', 'Gomez', 'Martinez', todos parten con mayuscula.
    'tipo_cancer' de tipo varchar: corresponde a la zona afectada del paciente. Algunos ejemplos de entradas son: 'Cáncer de Mama', 'Cáncer de Pulmón', 'Cáncer de Colon', 'Cáncer de Prostata', todos parten con mayuscula y llevan tilde.
    'categoria_cancer' de tipo int: da un numero del 1 al 5 respecto a la severidad.
    """,

    """
    En la tabla de nombre: "doctores"
    se almacena información referente a doctores que trabajan en la Fundación oncológica Arturo López Pérez.
    La información almacenada comprende las columnas:
    'id' de tipo int: esta es la clave primaria de la tabla.
    'nombre' de tipo varchar: este campo corresponde al nombre del doctor. Algunos ejemplos de entradas son: 'Juan', 'Ana', 'Pablo', 'Laura', todos parten con mayuscula.
    'sur' de tipo varchar: este campo  corresponde al apellido del doctor. Algunos ejemplos de entradas son: 'Perez', 'Gomez', 'Martinez', todos parten con mayuscula.
    'especialización' de tipo varchar: este campo contiene la especialidad del doctor. Ejemplos incluyen: 'Oncología', 'Pediatría', 'Ginecología', todos parten con mayúscula y llevan tildes.
    'hospital' de tipo varthcar: este campo contiene donde practica el doctor. Ejemplos de entradas incluyen: 'Hospital Central', 'Hospital del Norte' y 'Hospital del Sur', todos parten con mayuscula.
    """,

    """
    En la tabla de nombre "atenciones"
    es una tabla intermedia para las tablas 'pacientes' y 'doctores' donde se almacena información referente a qué doctor ha atendido a qué paciente.
    Las entradas siempre son uno a uno, vale decir en cada entrada un paciente es atendido por un doctor
    La información almacenada comprende las columnas:
    'id' de tipo int: esta es la clave primaria de la tabla.
    'id_doctor' de tipo int: es clave foránea de la tabla "doctores".
    'id_paciente' de tipo int: es clave foránea de la tabla "pacientes".

    """]

#def invoke_llm(messages: list, temperature=0, top_p=0.1):
#    question = messages[-1].get("content")
#    print("Pregunta:", question)

#    bedrock = boto3.client(service_name="bedrock-runtime", region_name="us-east-1")

#    model = Bedrock(model_id="anthropic.claude-v2:1", client=bedrock)  # Revisa modelos

#    bedrock_embeddings = BedrockEmbeddings(model_id="amazon.titan-embed-text-v1", client=bedrock)  # Revisa modelos

    # Crear vector store
#    vector_store = FAISS.from_texts(my_data, bedrock_embeddings)

    # Crear retriever
#    retriever = vector_store.as_retriever(search_kwargs={"k": 3})

#    results = retriever.get_relevant_documents(question)

#    results_string = [result.page_content for result in results]

    # Crear memoria
#    memory = ConversationBufferMemory()

    # Crear template
#    template = ChatPromptTemplate.from_messages(
#        [
    #         (
    #             "system",
    #             """Reconoce si lo que se te pregunta es una pregunta o simplemente una conversación. Si es una pregunta:
    #             Las siguientes son descripciones de una tabla y sus campos en una base de datos:

    #             {context}.

    #             Con esta información, necesito que traduzcas consultas en lenguaje natural a consultas SQL.
    #             No respondas con nada más que el SQL generado, un ejemplo de SQL es: "SELECT * FROM pacientes;", fíjate como NO hay '\n' en la respuesta. Tampoco agregues cordialidades o explicaciones, responde solo con SQL.
    #             Si se te pide información que no está en la tabla no la agregues a la consulta, responde lo que puedas, pero no des explicaciones, responde solo con SQL.
    #             Si se te pide modificar la base de datos, indica que no lo tienes permitido, este es el único caso donde puedes no usar SQL.

    #             En caso de que sea una conversación, responde indicando qué eres y cuál es tu función, la cual es ´Soy un asistente virtual que tiene como fin recibir preguntas referentes a la información de la base de datos de FALP, por favor formula tu pregunta´, en caso de que la conversación siga
    #             debes seguir respondiendo con mensajes que orienten al usuario a hacer una pregunta en la base de datos.
    #             """
    #         ),
    #         (
    #             "user",
    #             "{input}"
    #         ),
    #     ]
    # )

    # chain = template.pipe(model)
    # #chain = ConversationChain(llm=model, prompt=template)#, memory=memory)

    # response = chain.invoke({"input": question, "context": results_string})

    # # Guardar memoria
    # memory.save_context({"input": question}, {"output": response})

    # return response

def invoke_llm(messages: list, temperature=0, top_p=0.1):
    print(messages)
    question = messages[len(messages)-1].get("content")
    
    bedrock = boto3.client(service_name="bedrock-runtime", region_name="us-east-1")

    model = Bedrock(model_id="anthropic.claude-v2:1", client=bedrock) # Revisar modelos

    bedrock_embeddings = BedrockEmbeddings(model_id="amazon.titan-embed-text-v1", client=bedrock) # Revisar modelos

    # create vector store
    vector_store = FAISS.from_texts(my_data, bedrock_embeddings)

    # create retriever
    retriever = vector_store.as_retriever(
        search_kwargs={"k": 3}  # maybe we can add a score threshold here?
    )

    results = retriever.get_relevant_documents(question)

    results_string = []
    for result in results:
        results_string.append(result.page_content)
    
    # build template:
    template = ChatPromptTemplate.from_messages(
        [
        (

            "assistant",
            """Reconoce si lo que se te pregunta es una pregunta o simplemente una conversacion. si es una pregunta:Las siguientes son descripciones de una tabla y sus campos en una base de datos

            {context}.

            Con esta información, necesito que traduzcas consultas en lenguaje natural a consultas SQL.
            No respondas con nada más que el SQL generado, un ejemplo de SQL es: "SELECT * FROM pacientes;", fijate como NO hay '\n' en la respuesta. Tampoco agregues cordialidades o explicaciones, responde solo con SQL.
            Si se te pide informacion que no esta en la tabla no la agregues a la consulta, responde lo que puedas, pero no des explicaciones, responde solo con SQL.
            Si se te pide modificar la base de datos, indica que no lo tienes permitido, este es el único caso donde puedes no usar SQL.

            En caso de que sea una conversacion, respondes indicando qué eres y cuál es tu función, la cual es 'Soy un asistente virtual que tiene como fin recibir preguntas referentes a la informacion de la base de datos de FALP, por favor formula tu pregunta', en caso de que la conversacion siga
            debes seguir respondiendo con mensajes que orienten al usuario a hacer una pregunta en la base de datos. 
            """
        ),
        (
            "human",
            
            """
            {chat_history}
            {input}
            """
        ),
    ]
    )

    memory = ConversationBufferMemory(memory_key="chat_history")

    chain = LLMChain(llm=model, prompt=template, memory=memory)

    response = chain.invoke({"input": question, "context": results_string})
    return response


def invoke_llm_viejo(messages: list, system_prompt: str, temperature=0.1, top_p=0.1):
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
    
    response = invoke_llm(messages=messages)
    # invoca llm
    conversation_helper.insert_message(conversation_id, "assistant", response)

    # retorna estructura para leer desde backend-frontend 
    return {"response": response, "conversation_id": conversation_id}
