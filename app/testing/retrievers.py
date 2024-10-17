import boto3
import faiss
import numpy as np

from typing import Optional
from langchain_aws import BedrockEmbeddings, ChatBedrock
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.vectorstores import FAISS
from langchain_core.output_parsers import StrOutputParser
from langchain.chains import create_retrieval_chain, create_history_aware_retriever
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain.schema import Document

import time

from app.dependencies import get_settings
settings = get_settings()

def rag_retriever_titan_v1(rag_data: list, formatted_human_input: str, radio_busqueda: Optional[float] = 0.4, embeddings_model: Optional[str] = "amazon.titan-embed-text-v1"):
    start_time = time.time()
    documents = [Document(page_content=i) for i in rag_data]
    
    bedrock = boto3.client(service_name="bedrock-runtime", region_name=settings.aws_default_region)
    bedrock_embeddings = BedrockEmbeddings(model_id=embeddings_model, client=bedrock)

    document_embedding = bedrock_embeddings.embed_documents(texts=rag_data)
    question_embedding = bedrock_embeddings.embed_query(formatted_human_input)

    document_array = np.array(document_embedding)
    document_array_norm = document_array/np.linalg.norm(document_array, axis=1, keepdims=True)

    question_array = np.array(question_embedding)
    question_array_norm = question_array/np.linalg.norm(question_array, keepdims= True)
    question_array_norm = question_array_norm.reshape(1, -1)

    index = faiss.IndexFlatIP(document_array_norm.shape[1])
    index.add(document_array_norm)

    index_start_time = time.time()
    lims, D, I = index.range_search(question_array_norm, radio_busqueda)
    #print("e", lims, D, I)
    index_end_time = time.time()

    filtered_documents = [] 
    distancias = []# no es necesario, solo debuggeo
    for i in range(len(I)):
        filtered_documents.append(documents[i])
        distancias.append(D[i])#
    
    for_start_time = time.time()
    docs_retornados = []
    for doc in filtered_documents:
        docs_retornados.append(str(doc)[len("    En la tabla de nombre:             f "):len("    En la tabla de nombre:             f ")+9])#lol
    for_end_time = time.time()
    
    vector_start_time = time.time()
    vectorstore = FAISS.from_documents(documents=filtered_documents, embedding=bedrock_embeddings)
    retriever = vectorstore.as_retriever()
    end_time = time.time()
    tiempo_index = str(index_end_time - index_start_time).replace(".", ",")
    tiempo_vector = str(end_time - vector_start_time).replace(".", ",")
    tiempo_total = str(end_time - start_time - (for_end_time - for_start_time)).replace(".",",")

    return vectorstore,embeddings_model, formatted_human_input,len(docs_retornados), docs_retornados, distancias, tiempo_index, tiempo_vector, tiempo_total


def rag_retriever_titan_v2(rag_data: list, formatted_human_input: str, radio_busqueda: Optional[float] = 0.4, embeddings_model: Optional[str] = "amazon.titan-embed-text-v2:0"):
    start_time = time.time()
    documents = [Document(page_content=i) for i in rag_data]
    
    bedrock = boto3.client(service_name="bedrock-runtime", region_name=settings.aws_default_region)
    bedrock_embeddings = BedrockEmbeddings(model_id=embeddings_model, client=bedrock)

    document_embedding = bedrock_embeddings.embed_documents(texts=rag_data)
    question_embedding = bedrock_embeddings.embed_query(formatted_human_input)

    document_array = np.array(document_embedding)
    document_array_norm = document_array/np.linalg.norm(document_array, axis=1, keepdims=True)

    question_array = np.array(question_embedding)
    question_array_norm = question_array/np.linalg.norm(question_array, keepdims= True)
    question_array_norm = question_array_norm.reshape(1, -1)

    index = faiss.IndexFlatIP(document_array_norm.shape[1])
    index.add(document_array_norm)

    index_start_time = time.time()
    lims, D, I = index.range_search(question_array_norm, radio_busqueda)
    #print("e", lims, D, I)
    index_end_time = time.time()

    filtered_documents = [] 
    distancias = []# no es necesario, solo debuggeo
    for i in range(len(I)):
        filtered_documents.append(documents[i])
        distancias.append(D[i])#
    
    for_start_time = time.time()
    docs_retornados = []
    for doc in filtered_documents:
        docs_retornados.append(str(doc)[len("    En la tabla de nombre:             f "):len("    En la tabla de nombre:             f ")+9])#lol
    for_end_time = time.time()
    
    vector_start_time = time.time()
    vectorstore = FAISS.from_documents(documents=filtered_documents, embedding=bedrock_embeddings)
    retriever = vectorstore.as_retriever()
    end_time = time.time()
    tiempo_index = str(index_end_time - index_start_time).replace(".", ",")
    tiempo_vector = str(end_time - vector_start_time).replace(".", ",")
    tiempo_total = str(end_time - start_time - (for_end_time - for_start_time)).replace(".",",")

    return vectorstore,embeddings_model, formatted_human_input,len(docs_retornados), docs_retornados, distancias, tiempo_index, tiempo_vector, tiempo_total
