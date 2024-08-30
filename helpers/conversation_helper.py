import json
from datetime import datetime
from typing import Union
from handlers.DBORMHandler import DB_ORM_Handler
from models.conversationObject import ConversationObject
from models.messageObject import MessagesObject
from sqlalchemy import desc

# Todo lo relacionado a conversaciones y mensajes

def new_conversation(user_id: int):
    """
    Función para iniciar una conversación. Inserta una nueva conversación. Retorna el id de la conversación
    """
    with DB_ORM_Handler() as db:
        Conversation = ConversationObject()
        Conversation.user_id = user_id
        db.createTable(Conversation)
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
    Message.message = json.dumps(message)
    Message.type = type
    with DB_ORM_Handler() as db:
        db.createTable(Message)
        db.saveObject(Message)

def get_messages(conversation_id: int):
    """
    Obtiene los mensajes enviados en una conversación
    """
    with DB_ORM_Handler() as db:
        messages = db.getObjects(
            MessagesObject, 
            MessagesObject.conversation_id == conversation_id,
            MessagesObject.type == 'conversation',
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
            columns = [ConversationObject.id, ConversationObject.name, ConversationObject.created_at]
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
        return [json.loads(message.get("message")) for message in messages]

def get_last_query(conversation_id: int):
    """
    Obtiene la última query de la conversación
    """
    with DB_ORM_Handler() as db:
        messages = db.getObjects(
            MessagesObject, 
            MessagesObject.conversation_id == conversation_id,
            MessagesObject.type == 'query',
            defer_cols=[],
            order_by=[desc(MessagesObject.id)],
            columns=[MessagesObject.message]
        )
        if messages:
            message = messages[0]
            return json.loads(message.get("message")).get("content")
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
        return json.loads(messages[0].get("message"))