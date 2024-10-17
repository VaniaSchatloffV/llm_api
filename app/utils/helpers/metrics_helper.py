import json
from typing import Optional
from app.dependencies import get_settings

from app.models.metrics import MetricObject
from app.models.tokens import TokenObject
from app.models.chat import ConversationObject
from app.utils.helpers import tokens_helper
from app.crud.DBORMHandler import DB_ORM_Handler

settings = get_settings()

def get_metrics(conversation_id:int):
    ''' Funcion que obtiene las metricas de los llm'''
    input_tokens, output_tokens = tokens_helper.get_tokens(conversation_id=conversation_id)

    return {
        "Temperatura":settings.llm_temperature, 
        "Top P":settings.llm_top_p, 
        "Modelo LLM identificador de entrada":settings.llm_identify_model, 
        "Modelo LLM experto SQL":settings.llm_sql_model, 
        "Modelo LLM identificador NL-SQL":settings.llm_recognize_model, 
        "Modelo LLM corrector SQL":settings.llm_fix_model, 
        "Modelo LLM traductor data a NL":settings.llm_translate_model,
        "Modelo LLM diseñador de gráfico":settings.llm_graph_gen_model,
        "Modelo LLM experto SQL para gráfico":settings.llm_sql_graph_model,
        "Tokens de entrada":input_tokens,
        "Tokens de salida":output_tokens,
        "Tiempo de ejecución promedio":get_time_difference_between_messages(conversation_id)
        }



def upload_metric(conversation_id: int, questions: dict, calification: int):
    metric = MetricObject()
    metric.conversation_id = conversation_id
    metric.data = questions
    metric.metrics = get_metrics(conversation_id)
    metric.calification = calification
    with DB_ORM_Handler() as db:
        db.saveObject(metric)
        db.updateObjects(
            ConversationObject,
            ConversationObject.id == conversation_id,
            qualified = True
        )

def count_metrics():
    with DB_ORM_Handler() as db:
        total = db.countObjects(MetricObject)
        return total

def get_time_difference_between_messages(conversation_id : int):
    query = """
    WITH query_messages AS (
    SELECT
        id,
        conversation_id,
        message,
        created_at
    FROM messages
    WHERE type = 'response'
    ),
    question_messages AS (
        SELECT
            id,
            conversation_id,
            created_at
        FROM messages
        WHERE type = 'conversation' AND CAST(message as varchar) LIKE '%"user"%'
    ),
    join_query_question AS (
        SELECT
            question.conversation_id,
            query.created_at as created_at_query,
            question.created_at as created_at_question,
            ROW_NUMBER() OVER (PARTITION BY query.id ORDER BY question.id DESC) AS row_num
        FROM query_messages query
        JOIN question_messages question ON question.conversation_id = query.conversation_id AND question.id < query.id
        JOIN conversations c ON c.id = query.conversation_id
    )
    SELECT
        AVG(EXTRACT(EPOCH FROM (created_at_query - created_at_question))) as "tiempo_ejecucion"
    FROM join_query_question
    WHERE row_num = 1 AND conversation_id = {conversation_id}
    GROUP BY conversation_id;
    """

    formatted_query = query.format(conversation_id=conversation_id)
    with DB_ORM_Handler() as db:
        resp = db.query(formatted_query, return_data=True)

    return resp.pop().get("tiempo_ejecucion")

def get_table(offset: Optional[int] = None, limit: Optional[int] = None, order_by: Optional[str] = None, order_way: Optional[str] = None):
    if limit is None:
        limit = 10
    if offset is None:
        offset = 0
    order = [MetricObject.id.desc()]
    if order_by == "user_id":
        if order_way == "asc":
            order = [ConversationObject.user_id.asc()]
        else:
            order = [ConversationObject.user_id.desc()]
    if order_by == "conversation_id":
        if order_way == "asc":
            order = [ConversationObject.id.asc()]
        else:
            order = [ConversationObject.id.desc()]
    if order_by == "metric_id":
        if order_way == "asc":
            order = [MetricObject.id.asc()]
        else:
            order = [MetricObject.id.desc()]
    with DB_ORM_Handler() as db:
        results = db.getObjects(
            MetricObject,
            columns = [
                MetricObject.id.label("Id métrica"),
                ConversationObject.user_id.label("Id usuario"),
                ConversationObject.id.label("Id conversación"),
                MetricObject.calification.label("Calificación (valor máximo 5)"),
                MetricObject.data.label("Preguntas"),
                MetricObject.metrics.label("Métricas")
                ],
            join_conditions=[(ConversationObject, MetricObject.conversation_id == ConversationObject.id)],
            order_by=order,
            limit=limit,
            offset=offset
        )
            
    return results


def get_metric_table(limit: Optional[int] = None, offset: Optional[int] = 0, order_by: Optional[str] = None, order_way: Optional[str] = None):
    total = count_metrics()
    if offset >= total:
        next_offset = None
    else:
        next_offset = offset + limit
        if next_offset >= total:
            next_offset = None
    return {"data" : get_table(offset, limit, order_by, order_way), "total": total, "next_offset": next_offset}