import json
import sqlparse
from datetime import datetime
from typing import Optional, Union
from app.crud.DBORMHandler import DB_ORM_Handler
from app.models.chat import ConversationObject, MessagesObject
from sqlalchemy import desc

# Todo lo relacionado a conversaciones y mensajes

def new_conversation(user_id: int):
    """
    Función para iniciar una conversación. Inserta una nueva conversación. Retorna el id de la conversación
    """
    with DB_ORM_Handler() as db:
        Conversation = ConversationObject()
        Conversation.user_id = user_id
        conversation_id = db.saveObject(p_obj=Conversation, get_obj_attr=True, get_obj_attr_name="id")
        return conversation_id


def insert_message(conversation_id: int, role: str, content: Union[list, str], type: str = "conversation"):
    """
    Función para almacenar mensaje.
    conversation_id: id de la conversación.
    role: user o assistant (string)
    content: el contenido del mensaje
    """
    message = {
        "role": role,
        "content": content
    }
    Message = MessagesObject()
    Message.conversation_id = conversation_id
    Message.message = message
    Message.type = type
    with DB_ORM_Handler() as db:
        db.saveObject(Message)


def get_messages(conversation_id: int):
    """
    Obtiene los mensajes enviados en una conversación
    """
    with DB_ORM_Handler() as db:
        messages = db.getObjects(
            MessagesObject, 
            MessagesObject.conversation_id == conversation_id,
            MessagesObject.type.in_(['conversation', 'option', 'file', 'response']),
            defer_cols=[],
            order_by=[MessagesObject.id],
            columns = [MessagesObject.message]
        )
        if not messages:
            return []
        return [i.get("message") for i in messages]


def get_conversations(user_id: int):
    """
    Obtiene las conversaciones de un usuario ordenadas por id en orden descendente
    """
    with DB_ORM_Handler() as db:
        conversations = db.getObjects(
            ConversationObject,
            ConversationObject.user_id == user_id,
            defer_cols=[],
            order_by=[ConversationObject.id.desc()],
            columns = [ConversationObject.id, ConversationObject.name, ConversationObject.created_at, ConversationObject.qualified]
        )
        if not conversations:
            return []
        return conversations


def get_messages_for_llm(conversation_id: int):
    """
    Obtiene los mensajes enviados en una conversación que sean de tipo 'conversation' o 'query'
    """
    with DB_ORM_Handler() as db:
        messages = db.getObjects(
            MessagesObject,
            MessagesObject.conversation_id == conversation_id,
            MessagesObject.type.in_(['conversation', 'query']),
            defer_cols=[],
            order_by=[MessagesObject.id],
            columns=[MessagesObject.message]
        )
        if not messages:
            return []
        return [message.get("message") for message in messages]


def get_last_query(conversation_id: int):
    """
    Obtiene la última query de la conversación
    """
    with DB_ORM_Handler() as db:
        messages = db.getObjects(
            MessagesObject, 
            MessagesObject.conversation_id == conversation_id,
            MessagesObject.type.in_(['query_review', 'query']),
            defer_cols=[],
            order_by=[desc(MessagesObject.id)],
            columns=[MessagesObject.message]
        )
        if messages:
            message = messages[0]
            return message.get("message").get("content")
        return []


def get_option_messages(conversation_id: int):
    """
    Obtiene el último mensaje de tipo 'option' enviado en una conversación
    """
    with DB_ORM_Handler() as db:
        messages = db.getObjects(
            MessagesObject,
            MessagesObject.conversation_id == conversation_id,
            MessagesObject.type == 'option',
            defer_cols=[],
            order_by=[desc(MessagesObject.id)],
            columns=[MessagesObject.message],
            limit=1
        )
        if not messages:
            return []
        return messages[0].get("message")


def change_conversation_name(conversation_id: int, name: str):
    """
    Cambia el nombre de una conversación
    """
    if name == "":
        name = None
    with DB_ORM_Handler() as db:
        rs = db.updateObjects(
            ConversationObject,
            ConversationObject.id == conversation_id,
            name = name
        )
        return rs


def get_conversation_table(offset: Optional[int] = None, limit: Optional[int] = None, order_by: Optional[str] = None, order_way: Optional[str] = None):
    if limit is None:
        limit = 10
    if offset is None:
        offset = 0
    if order_by is None:
        order_by = "conversation_id"
    get_conversation_attr = f"""
        WITH query_messages AS (
            SELECT
                id,
                conversation_id,
                message
            FROM messages
            WHERE type = 'query'
        ),
        question_messages AS (
            SELECT
                id,
                conversation_id,
                message
            FROM messages
            WHERE type = 'conversation' AND CAST(message as varchar) LIKE '%"user"%'
        ),
        join_query_question AS (
            SELECT
                query.message as mq,
                question.message as mqq,
                question.conversation_id,
                c.user_id,
                ROW_NUMBER() OVER (PARTITION BY query.id ORDER BY question.id DESC) AS row_num
            FROM query_messages query
            JOIN question_messages question ON question.conversation_id = query.conversation_id AND question.id < query.id
            JOIN conversations c ON c.id = query.conversation_id
        )
        SELECT
            conversation_id as "Id conversación",
            user_id as "Id usuario",
            mqq->>'content' as "Mensaje inicial",
            mq::json->'content'->>'query' as "Consulta generada"
        FROM join_query_question
        WHERE row_num = 1
        ORDER BY {order_by} {order_way}
        LIMIT {limit}
        OFFSET {offset}
    """
    with DB_ORM_Handler() as db:
        data = db.query(get_conversation_attr, return_data=True)
        for i in range(len(data)):
            data[i]["Consulta generada"] = sqlparse.format(data[i].get("Consulta generada"), reindent=True, keyword_case='upper')
        return data

def count_conversations():
    with DB_ORM_Handler() as db:
        total_conversations = db.countObjects(ConversationObject)
        return total_conversations