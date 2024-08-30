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
        DB_ORM_Handler.initialize(Conversation)
        conversation_id = DB_ORM_Handler.saveObject(Conversation, get_obj_attr=True, get_obj_attr_name="id")
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
    message_json = json.dumps(message)
    Message = MessagesObject()
    Message.conversation_id = conversation_id
    Message.message = message_json
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
            MessagesObject.type == 'conversation',
            defer_cols=[],
            order_by=[MessagesObject.id]
        )
        print(messages)
        # if not messages:
        #     return []
        # messages = [item.message for item in messages]
        # return messages

def get_messages(conversation_id: int):
    """
    Obtiene los mensajes enviados en una conversación
    """
    with DB_ORM_Handler() as db:
        messages = db.getObjects(
            MessagesObject, 
            MessagesObject.conversation_id == conversation_id,
            MessagesObject.type.in_(['conversation', 'query']),
            defer_cols=[],
            order_by=[MessagesObject.id]
        )
        print(messages)
        # if not messages:
        #     return []
        # messages = [item.message for item in messages]
        # return messages
    

def get_conversations(user_id: int):
    """
    Obtiene las conversaciones de un usuario ordenadas por id en orden descendente
    """
    with DB_ORM_Handler() as db:
        conversations = db.getObjects(
            ConversationObject,
            ConversationObject.user_id == user_id,
            defer_cols=[],
            order_by=[ConversationObject.id.desc()]
        )
        print(conversations)
        if not conversations:
            return []
        return conversations

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
            limit=1
        )
        print(messages)
        if messages:
            message = messages[0]
            return message.content
        return None

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
            limit=1
        )
        if not messages:
            return []
        return messages[0].message