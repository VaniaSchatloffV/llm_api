import os
import boto3
import json
import numpy as np
import pandas as pd

from langchain_aws import BedrockLLM, BedrockEmbeddings, ChatBedrock
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnablePassthrough
from langchain_community.vectorstores import FAISS
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain
from langchain.chains import LLMChain
from langchain_core.output_parsers import StrOutputParser
from langchain.chains import create_retrieval_chain, create_history_aware_retriever
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.messages import AIMessage, HumanMessage


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


def invoke_llm(question ,messages: list, temperature=0, top_p=0.1):
    bedrock = boto3.client(service_name="bedrock-runtime", region_name=settings.aws_default_region)

    # model = BedrockLLM(
    #     model_id="anthropic.claude-v2:1"
    # )

    model = ChatBedrock(
        model_id="anthropic.claude-3-sonnet-20240229-v1:0"
    )

    bedrock_embeddings = BedrockEmbeddings(model_id="amazon.titan-embed-text-v1", client=bedrock) # Revisar modelos
    # create vector store
    vector_store = FAISS.from_texts(my_data, bedrock_embeddings)
    # create retriever
    retriever = vector_store.as_retriever(
        search_kwargs={"k": 3}  # maybe we can add a score threshold here?
    )
    
    results = retriever.invoke(question)
    results_string = []
    for result in results:
        results_string.append(result.page_content)
    
    system_prompt = """
        Las siguientes son descripciones de una tabla y sus campos en una base de datos:
        {context}
        Estos campos pueden contener valores diferentes a los dados, es importante que uses la información entregada por el usuario en el formato dado.
        Estas son los únicos campos de las tablas. Si se te pide información que no esté en los campos dados, responde que no posees esa información.

        Con esta información, necesito que traduzcas consultas en lenguaje natural a consultas SQL.
        No respondas con nada más que el SQL generado, un ejemplo de SQL es: "SELECT * FROM pacientes;". Tampoco agregues cordialidades o explicaciones, responde solo con SQL.
        Si se te pide informacion que no esta en la tabla no la agregues a la consulta, responde lo que puedas, pero no des explicaciones, responde solo con SQL.
        Si se te pide modificar la base de datos, indica que no lo tienes permitido, este es el único caso donde puedes no usar SQL.

        En caso de que sea una conversacion, respondes indicando qué eres y cuál es tu función, la cual es 'Soy un asistente virtual que tiene como fin recibir preguntas referentes a la informacion de la base de datos de FALP, por favor formula tu pregunta', en caso de que la conversacion siga
        debes seguir respondiendo con mensajes que orienten al usuario a hacer una pregunta en la base de datos.
    """

    # build template:
    prompt = ChatPromptTemplate.from_messages(
        [
        (
            "system", system_prompt
        ),
        MessagesPlaceholder("chat_history"),
        (
            "human", "{input}"
        ),
    ]
    )
    history_aware_retriever = create_history_aware_retriever(model, retriever, prompt)
    question_answer_chain = create_stuff_documents_chain(model, prompt)
    rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)

    messages.pop()
    response = rag_chain.invoke({"context": retriever, "input": question, "chat_history": messages})
    return response 



def send_prompt(question, messages: list):
    response = invoke_llm(question=question, messages=messages)
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
    messages_for_llm = []
    for mess in messages:
        if mess.get("role") == "user":
            content = mess.get("content")
            messages_for_llm.append(HumanMessage(content=content))
        elif mess.get("role") == "assistant":
            content = mess.get("content")
            messages_for_llm.append(AIMessage(content=content))
    
    resp = send_prompt(prompt , messages_for_llm)
    conversation_helper.insert_message(conversation_id, "assistant", resp.get("answer"))
    return {"response": resp.get("answer"), "conversation_id": conversation_id}



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
    #AGREGAR PARSER

    response_SQL_NL = recognize_SQL_LLM(resp)
    if response_SQL_NL == "SQL": 
        conversation_helper.insert_message(conversation_id, "assistant", resp, "query")
        with DB_ORM_Handler() as db:
            data = db.query(resp, return_data=True)

            #REVISAR SI DATA ES SUFICIENTEMENTE CHICO PARA SER RECIBIDO POR PROMPT 
            #INVESTIGAR SI EL OUTPUT TOKENS DEL JC invoca a la llm
            #else REVISAR API AWS BEDROCK

            #SI SE PUEDE, ENTRA A LLM A TRADUCIRLA
            #ELIF SE VA A LA LOGICA DE EN Q FORMATO ---------

        resp = {"text": "¿En qué formato desea recibir la información?"}
        resp["options"] = file_helper.OPTIONS
        conversation_helper.insert_message(conversation_id, "assistant", resp, type="option")
        return {"response": resp, "conversation_id": conversation_id}

    conversation_helper.insert_message(conversation_id, "assistant", resp)
    return {"response": resp, "conversation_id": conversation_id}

def recognize_SQL_LLM(question, temperature=0, top_p=0.1):

    model = ChatBedrock(
        model_id="anthropic.claude-3-5-sonnet-20240620-v1:0"
    )

    system_prompt = """
Analiza el siguiente mensaje y determina si es completamente código SQL o si contiene lenguaje natural.

Responde 'SQL' solo si todo el mensaje es sintaxis SQL válida, sin ninguna palabra o frase que no sea parte del código SQL.
Responde 'NL' si el mensaje contiene cualquier palabra, frase, o parte en lenguaje natural que no sea sintaxis SQL, incluso si hay segmentos de SQL presentes.
Solo clasifica el mensaje.
    """

    # build template:
    prompt = ChatPromptTemplate.from_messages(
        [
        (
            "system", system_prompt
        ),
        (
            "human", "{input}"
        ),
    ]
    )

    chain = (
        prompt 
        | model
        | StrOutputParser()
        )

    response = chain.invoke({"input": question})
    return response 