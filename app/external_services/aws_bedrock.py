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


def invoke_rag_llm_with_memory(question,
                            rag_data: list,
                            system_prompt: str,
                            human_input: str,
                            llm_model: Optional[str] = "anthropic.claude-3-sonnet-20240229-v1:0",
                            embeddings_model: Optional[str] = "amazon.titan-embed-text-v1",
                            memory: Optional[list] = [],
                            parameters : Optional[dict] = {},
                            temperature=0,
                            top_p=0.1):
    bedrock = boto3.client(service_name="bedrock-runtime", region_name=settings.aws_default_region)
    
    model = ChatBedrock(
        model_id=llm_model,
        model_kwargs={"temperature": 0}
    )

    bedrock_embeddings = BedrockEmbeddings(model_id=embeddings_model, client=bedrock) # Revisar modelos
    
    vector_store = FAISS.from_texts(rag_data, bedrock_embeddings)
    
    retriever = vector_store.as_retriever(
        search_kwargs={"k": 3}
    )
    
    results = retriever.invoke(question)
    results_string = []
    for result in results:
        results_string.append(result.page_content)

    # build template:
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
    #Actualmente se ha probado pocas veces, pero tiene un funcionamiento de PMV
    model = ChatBedrock(
        model_id=model,
        model_kwargs={"temperature": temperature, "top_p": top_p}
    )

    # build template:
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