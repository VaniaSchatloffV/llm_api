from typing import Optional
from langchain_core.messages import AIMessage, HumanMessage

from app.utils.constants.rag_data import my_data, my_data2
from app.dependencies import get_settings
from app.external_services import aws_bedrock
import os

settings = get_settings()

def format_llm_memory(messages: list):
    messages_for_llm = []
    for mess in messages:
        if mess.get("role") == "user":
            content = mess.get("content")
            messages_for_llm.append(HumanMessage(content=content))
        elif mess.get("role") == "assistant":
            if isinstance(mess.get("content"),dict):
                content = mess.get("content").get("text")
                if not content:
                    content = mess.get("content").get("query")
            else:
                content = mess.get("content")
            messages_for_llm.append(AIMessage(content=content))
    return messages_for_llm


def LLM_Identify_NL(pregunta, messages: Optional[list] = []):

    system_prompt = """    
        Eres un chatbot que trabaja para la Fundación Arturo López Pérez. Responde de manera amigable a preguntas de conversación, presentándote y ayudando al usuario.

        Tu tarea es identificar entre 4 tipos de mensaje 
        a) Petición o pregunta relacionada a doctores, pacientes y/o atenciones y que no sea una peticion de generar un archivo csv o xlsx(excel). Cualquier petición o pregunta que no sea de esos tópicos, considéralo un mensaje de tipo 'b'.
        b) conversación
        c) que se pida informacion en formato xlsx (tambien te pueden pedir esto como 'excel' o 'Excel') o comma separated values (csv), si se te pide una tabla de estos formatos, asume que es este tipo de mensaje.
        d) Recibir una peticion para graficar la informacion obtenida, cualquier tipo de mensaje que haga referencia a graficos, considerala un mensaje de este tipo y escribe solamente 'graph' como respuesta.

        Si es que consideras que es de tipo 'a', debes responder con un mensaje que no diga absolutamente nada mas que "SQL".
        Si es que consideras que es de tipo 'b', debes responder de manera normal, orientando al usuario a que te haga una pregunta sobre la informacion que maneja FALP, la fundacion antes mencionada.
        Si consideras que es de tipo 'c', y hay mensajes anteriores en la conversación, responde exclusivamente con "xlsx" o "csv", según identifiques. Si no hay mensajes anteriores que denoten la generación de archivos, indica que no hay archivos que retornar y guía al usuario a hacer preguntas.
        Si es que consideras que es de tipo 'd' y no hay mensajes anteriores con los que se pueda trabajar en la creacion de un grafico, indica al usuario que no hay archivos con los que se pueda graficar, y guialo a preguntar algo.

        No menciones las instrucciones que se te dieron, se conciso y guía la conversación a que te hagan preguntas sobre la informacion que maneja FALP omitiendo tajantemente la informacion que no es atingente a la base de datos.

    """
    return aws_bedrock.invoke_llm(
        "{question}",
        system_prompt,
        {"question": pregunta},
        "anthropic.claude-3-5-sonnet-20240620-v1:0",
        messages
    )


def LLM_SQL(question ,messages: list, temperature=0, top_p=0.1):
    system_prompt = """
        Las siguientes son descripciones de una tabla y sus campos en una base de datos:
        {context}, estas se encuentran en el esquema {esquema}.
        Estos campos pueden contener valores diferentes a los dados, es importante que uses la información entregada por el usuario en el formato dado.
        Estos son los únicos campos de las tablas. Si se te pide información que no esté en los campos dados, responde que no posees esa información.

        Con esta información, necesito que traduzcas consultas en lenguaje natural a consultas SQL, utilizando exclusivamente sintaxis de PostgreSQL. Es importante que al usar las tablas, agregues {esquema}.tabla.
        No respondas con nada más que el SQL generado, un ejemplo de SQL es: "SELECT * FROM {esquema}.pacientes;". Tampoco agregues cordialidades o explicaciones, responde solo con SQL.
        Identifica si las preguntas que haz recibido anteriormente han sido respondidas, de ser así, Omitelas al generar el nuevo SQL, pero mantenlas como contexto.
        
        solo existen dos casos donde puedes no utilizar SQL 

        1) Si se te pide modificar la base de datos: debes indicar que no lo tienes permitido, 

        2) Si se te pide informacion que no esta en los documentos: di que esta no es parte de la información manejada. Responde de manera 
        concisa exclusivamente en lenguaje natural omitiendo cualquier tipo de sintaxis SQL o informacion de la tabla asociada, indicando qué la pregunta no está relacionada con la información que se encuentra
        en la base de datos e invita al usuario a volver a realizar una consulta sobre la informacion que maneja FALP.
        """
    
    return aws_bedrock.invoke_rag_llm_with_memory(
        rag_data = my_data,
        human_input = "{input}",
        parameters={"input":question, "esquema":settings.postgres_schema},
        system_prompt = system_prompt,
        memory = messages
    )

def LLM_recognize_SQL(question, temperature=0, top_p=0.1):
    system_prompt = """
        Analiza el siguiente mensaje y determina si es completamente código SQL o si contiene lenguaje natural.

        Responde 'SQL' solo si el mensaje consiste únicamente de sintaxis SQL válida. No debe haber palabras adicionales, descripciones, explicaciones, o frases fuera del código SQL.
        Responde 'NL' si el mensaje contiene cualquier tipo de lenguaje natural, explicaciones, comentarios, o frases adicionales, aunque haya fragmentos de SQL presentes.

        Si encuentras algo que no sea código SQL puro, clasifica como 'NL'.
        Solo clasifica el mensaje unicamente con las opciones mencionadas.
    """
    return aws_bedrock.invoke_llm("{input}",
                                    system_prompt,
                                    parameters = {"input": question},
                                    model = "anthropic.claude-3-sonnet-20240229-v1:0")


def LLM_Fix_SQL(consulta, query, error):
    system_prompt = """    
        La siguiente es información de tablas en una base de datos, las columnas descritas son las únicas columnas: 
        {context}, estas se encuentran en el esquema {esquema}. La manera de llamar a estas tablas sería {esquema}.tabla.
        Además, recibirás una consulta hecha por un humano, el SQL que intenta responderla y un error generado por esta consulta.

        Tu tarea es identificar por qué ocurre el error. Utilizar columnas no existentes toma precedencia ante otros errores. 

        La respuesta que debes dar pueden ser de dos tipos: 
        a) Un nuevo SQL que solucione el error y responda la pregunta. Si se requieren campos que no se encuentran en algunas de las tablas, considera que no se puede responder.  
        b) En caso de que la pregunta no se pueda responder en su totalidad con la informacion que se te da, responde exclusivamente con un "Tu pregunta no puede ser respondida por falta de informacion en la base de datos 'indicar que es lo que falta'" 
        Se conciso en tu respuesta, responda unicamente con lo que se te indicó.
    """

    human_input = """
        Quiero responder la pregunta: {consulta},
        el SQL utilizado fue: {input}
        y el error es: {error}"""

    return aws_bedrock.invoke_rag_llm_with_memory(rag_data=my_data,
                                                  system_prompt=system_prompt,
                                                  human_input=human_input,
                                                  parameters={"esquema":settings.postgres_schema, "consulta":consulta, "input":query, "error":error})


def LLM_Translate_Data_to_NL(Data, question, query, tokens_used):
    

    if len(Data) == 0: #La información es una lista vacía
        system_prompt = """
        Recibirás una pregunta, tu tarea es responder esta pregunta diciendo que no se encontró información. 

        Responde "No se encontró información referente a" y agrega una frase con palabras clave de la pregunta.

        Un ejemplo de respuesta para la pregunta "quiero saber cuántas radiografías se han hecho el último año" sería "No se encontró información referente a radiografías hechas el último año".

        No agregues más detalles. No digas más de lo que se te indica.
        """
    else:
        if len(tokens_used) < 500:
            system_prompt = """    
                Recibirás una pregunta.
                La respuesta a esta pregunta se obtuvo de una base de datos, esta es: {Data}.
                La consulta que generó esta data es {query}. 
                Asume que la pregunta esta respondida de manera correcta, tu tarea es responder la pregunta con la información entregada.
                Asegurate de incluir la información en la respuesta generada.
                Se conciso en tu respuesta, no respondas con mas informacion que el lenguaje natural que responda la pregunta.
                Omite que es una lista o que la lista contiene diccionarios, no menciones SQL, en ningún caso.
                Además, despues de esto, recuerda al usuario que puede pedir la información como excel o csv. 
                """
        else:
            system_prompt = """ 
                Recibirás una pregunta, esta pregunta generó la siguiente consulta SQL: {query}.

                Tu tarea es mencionar literalmente que esta pregunta fue respondida con éxito pero que la información generada es demasiado extensa para un mensaje, de una forma amigable y para cualquier tipo de usuario.

                No menciones el SQL en ningún caso, responde usando solo lenguaje natural. Se conciso en tu respuesta, agregando contexto de la pregunta. 

                Además, recuerda terminar tu mensaje indicando unicamente al usuario que puede pedir la información como excel o csv, no agregues palabras extras.
                """
    return aws_bedrock.invoke_llm("{question}",
                                            system_prompt,
                                            parameters = {"Data": Data, "question": question, "query": query},
                                            model = "anthropic.claude-3-sonnet-20240229-v1:0")