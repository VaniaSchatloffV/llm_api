import boto3
from typing import Optional

from langchain_aws import BedrockEmbeddings, ChatBedrock
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.vectorstores import FAISS
from langchain_core.output_parsers import StrOutputParser
from langchain.chains import create_retrieval_chain, create_history_aware_retriever
from langchain.chains.combine_documents import create_stuff_documents_chain

from app.dependencies import get_settings
settings = get_settings()

def rag_retriever(rag_data: list, embeddings_model: Optional[str] = "amazon.titan-embed-text-v1"):
    bedrock = boto3.client(service_name="bedrock-runtime", region_name=settings.aws_default_region)
    bedrock_embeddings = BedrockEmbeddings(model_id=embeddings_model, client=bedrock) # Revisar modelos
    vector_store = FAISS.from_texts(rag_data, bedrock_embeddings)
    
    retriever = vector_store.as_retriever(
        search_kwargs={"k": 3}
    )
    return retriever
    # Comentado ya que no se utiliza.
    # results = retriever.invoke(question)
    # results_string = []
    # for result in results:
    #     results_string.append(result.page_content)
    # return results_string


def invoke_rag_llm_with_memory(rag_data: list,
                            system_prompt: str,
                            human_input: str,
                            llm_model: Optional[str] = "anthropic.claude-3-sonnet-20240229-v1:0",
                            embeddings_model: Optional[str] = "amazon.titan-embed-text-v1",
                            memory: Optional[list] = [],
                            parameters : Optional[dict] = {},
                            temperature=0,
                            top_p=0.1):
    """
    Función que invoca LLM.
    - rag_data: lista con información para el RAG
    - system_prompt: string con prompt para el sistema. Debe incluir parámetro context para incluir RAG. Ejemplo: "Responde respecto a la siguiente información: {context}."
    - human_input: string que tenga el prompt del usuario. Puede incluir parámetros con {}. Un ejemplo es " Responde de manera cariñosa a {input} "
    - llm_model: modelo del LLM.
    - embeddings_model: modelo de embedding para el RAG.
    - memory: Lista con todos los mensajes enviados a la LLM. Incluye el mensaje actual.
    - parameters: Diccionario de parámetros para los prompts. Ejemplo: {"input" : "Hola, ¿como estas?"}.

    Nota: Al ser con RAG. la información del rag almacenada en un retriever se almacena en un parámetro llamado 'context'. Debe ser considerado en el system prompt si se desea incluir el RAG.
    """
    model = ChatBedrock(
        model_id=llm_model,
        model_kwargs={"temperature": temperature, "top_p": top_p}
    )
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system", system_prompt
            ),
            MessagesPlaceholder("chat_history"),
            (
                "human", human_input
            ),
        ]
    )
    retriever = rag_retriever(rag_data, embeddings_model)
    history_aware_retriever = create_history_aware_retriever(model, retriever, prompt)
    question_answer_chain = create_stuff_documents_chain(model, prompt)
    rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)
    if len(memory) != 0:
        memory.pop()
    parameters["context"] = retriever
    parameters["chat_history"] = memory
    response = rag_chain.invoke(parameters)
    return response



def invoke_llm(human_input: str,
                    system_prompt: str,
                    parameters: Optional[dict] = {},
                    model: Optional[str] ="anthropic.claude-3-sonnet-20240229-v1:0",
                    messages: Optional[list] = [],
                    temperature=0,
                    top_p=0.1):
    """
    Función que invoca LLM.
    - human_input: string que tenga el prompt del usuario. Puede incluir parámetros con {}. Un ejemplo es " Responde de manera cariñosa a {input} "
    - system_prompt: string con prompt para el sistema. Ejemplo: "Eres un analista de datos."
    - parameters: Diccionario de parámetros para los prompts. Ejemplo: {"input" : "Hola, ¿como estas?"}.
    - model: modelo del LLM.
    - messages: Lista con todos los mensajes enviados a la LLM. Incluye el mensaje actual.
    """
    model = ChatBedrock(
        model_id=model,
        model_kwargs={"temperature": temperature, "top_p": top_p}
    )
    prompt = ChatPromptTemplate.from_messages(
        [
        (
            "system", system_prompt
        ),
        MessagesPlaceholder("chat_history"),
        (
            "human", human_input
        ),
        ]
    )
    chain = (
        prompt 
        | model
        | StrOutputParser()
        )
    if len(messages) != 0:
        messages.pop()
    parameters["chat_history"] = messages
    response = chain.invoke(parameters)
    return response 