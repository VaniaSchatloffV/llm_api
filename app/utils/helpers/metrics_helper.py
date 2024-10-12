import json

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