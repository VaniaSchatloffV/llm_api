import json
from typing import Optional

from app.models.metrics import MetricObject
from app.models.chat import ConversationObject
from app.crud.DBORMHandler import DB_ORM_Handler

def get_metrics():
    # Funcion que debe obtener las metricas de los llm
    return {}


def upload_metric(conversation_id: int, questions: dict, calification: int):
    metric = MetricObject()
    metric.conversation_id = conversation_id
    metric.data = questions
    metric.metrics = get_metrics()
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
    with DB_ORM_Handler() as db:
        results = db.getObjects(
            MetricObject,
            columns = [MetricObject.id,ConversationObject.id,ConversationObject.user_id,MetricObject.calification,MetricObject.data],
            join_conditions=[(ConversationObject, MetricObject.conversation_id == ConversationObject.id)],
            order_by=order,
            limit=limit
        )
            
    return results


def get_metric_table(limit: Optional[int] = None, offset: Optional[int] = None, order_by: Optional[str] = None, order_way: Optional[str] = None):
    # total = count_metrics()
    # if offset >= total:
    #     next_offset = None
    # else:
    #     next_offset = offset + limit
    #     if next_offset >= total:
    #         next_offset = None
    offset = None
    limit = None
    order_by = None
    order_way = None
    total = None
    next_offset = None
    return {"data" : get_table(offset, limit, order_by, order_way), "total": total, "next_offset": next_offset}