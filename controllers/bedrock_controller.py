import os
import boto3
import json
import numpy as np
import pandas as pd

from langchain_community.llms import Bedrock
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_community.embeddings import BedrockEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain
from langchain.chains import LLMChain
from langchain_core.output_parsers import StrOutputParser



from botocore.exceptions import ClientError

from configs.config import get_settings
from handlers.DBORMHandler import DB_ORM_Handler
from helpers import conversation_helper, file_helper

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
    'id_atencion' de tipo int: esta es la clave primaria de la tabla.
    'id_doctor' de tipo int: es clave foránea de la tabla "doctores".
    'id_paciente' de tipo int: es clave foránea de la tabla "pacientes".

    """]


def invoke_llm(messages: list, temperature=0, top_p=0.1):
    #memory = ConversationBufferMemory(memory_key="chat_history")
    print(messages)
    question = messages[len(messages)-1].get("content")
    print("hola")
    bedrock = boto3.client(service_name="bedrock-runtime", region_name="us-east-1")
    print("hola2")
    model = Bedrock(model_id="anthropic.claude-v2:1", client=bedrock) # Revisar modelos
    print("hola3")
    bedrock_embeddings = BedrockEmbeddings(model_id="amazon.titan-embed-text-v1", client=bedrock) # Revisar modelos
    print("hola4")
    # create vector store
    vector_store = FAISS.from_texts(my_data, bedrock_embeddings)
    print("hola5")
    # create retriever
    retriever = vector_store.as_retriever(
        search_kwargs={"k": 3}  # maybe we can add a score threshold here?
    )
    
    print("hola6")
    results = retriever.get_relevant_documents(question)
    print("hola7")
    results_string = []
    for result in results:
        results_string.append(result.page_content)
    print(results_string)
    print("hola8")
    # build template:
    template = ChatPromptTemplate.from_messages(
        [
        (

            "assistant",
            #"""Reconoce si lo que se te pregunta es una pregunta o simplemente una conversacion. si es una pregunta
            """
            Las siguientes son descripciones de una tabla y sus campos en una base de datos.
            {context}
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
            Estos son mensajes anteriores de esta misma conversacion: 
            {messages}
            Y este es mi mensaje nuevo al que debes responder:
            {input}
            """
        ),
    ]
    )
    print("hola9")
    print(type(messages))
    print(type(messages[0]))
    print(type(results_string))
    msg = {}
    for i in range(len(messages)):
        msg = messages[i]
    print(msg)
    #print(memory)
    results_string_combined = "\n".join(results_string)

    retrieval_chain = (
    {"context": retriever, "messages": RunnablePassthrough, "input": RunnablePassthrough()}
    | template
    | model
    )
    
    print("hola10")
    #messages= template.format_messages(context = results_string)
    #chain = LLMChain(llm=model, prompt=messages, memory=memory)
    

    response = retrieval_chain.invoke(question) #+ "\n context:" + str(results_string)})
    print("hola11")
    return response 



def send_prompt(messages: list):
    response = invoke_llm(messages=messages)
    return response


def send_prompt2(messages: list):
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

    conversation_helper.insert_message(conversation_id, "user", prompt)
    
    # Se obtienen mensajes anteriores para la llm
    messages = conversation_helper.get_messages_for_llm(conversation_id)
    print("hola estoy aqui", messages)
   
    print("entre al try")
    resp = send_prompt(messages)
    print(resp)
    conversation_helper.insert_message(conversation_id, "assistant", resp)
    return {"response": resp, "conversation_id": conversation_id}



def send_prompt_and_process_vania(prompt: str, conversation_id: int, user_id: int):
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
        try:
            if last_message.get("role") == "assistant":
                query = conversation_helper.get_last_query(conversation_id)
                with DB_ORM_Handler() as db:
                    data = db.query(query, return_data=True)
                file_id = file_helper.to_file(prompt, data)
                resp = {"text": "El archivo ya está listo", "file_id": file_id, "file_type": prompt}
                conversation_helper.insert_message(conversation_id, "assistant", resp, type="file")
                return {"response": resp, "conversation_id": conversation_id}
        except Exception as e:
            # AQUI AGREGAR CUANDO LA COSA FALLA Y PREGUNTAR POR QUÉ
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

