import json
from datetime import datetime
from typing import Union
from handlers.DBHandler import DBHandler

# Todo lo relacionado a conversaciones y mensajes

def new_conversation(user_id: int):
    """
    Función para iniciar una conversación. Inserta una nueva conversación. Retorna el id de la conversación
    """
    with DBHandler() as db:
        insert_new_conversation = """
            INSERT INTO conversations(user_id) VALUES (%s)
        """
        conversation_id = db.insert_get_id(insert_new_conversation, (user_id,))
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
    insert_new_message = """
        INSERT INTO messages (conversation_id, message, type)
        VALUES (%s, %s, %s)
    """
    with DBHandler() as db:
        db.execute(insert_new_message, (conversation_id, message_json, type))

def get_messages(conversation_id: int):
    """
    Obtiene los mensajes enviados en una conversación
    """
    get_messages_query = """
        SELECT message
        FROM messages
        WHERE conversation_id = %s AND type = 'conversation'
        ORDER BY id
    """
    with DBHandler() as db:
        messages = db.select(get_messages_query, (conversation_id,))
        if messages is None:
            return []
        messages = [item.get("message") for item in messages]
        return messages

def get_messages_for_llm(conversation_id: int):
    """
    Obtiene los mensajes enviados en una conversación
    """
    get_messages_query = """
        SELECT message
        FROM messages
        WHERE conversation_id = %s AND type in ('conversation','query')
        ORDER BY id
    """
    with DBHandler() as db:
        messages = db.select(get_messages_query, (conversation_id,))
        if messages is None:
            return []
        messages = [item.get("message") for item in messages]
        return messages
    

def get_conversations(user_id: int):
    get_conversations_query = """
        SELECT id, name, created_at
        FROM conversations
        WHERE user_id = %s
        ORDER BY id DESC
    """
    with DBHandler() as db:
        conversations = db.select(get_conversations_query, (user_id,))
        if conversations is None:
            return []
        return conversations

def get_last_query(conversation_id: int):
    """
    Obtiene ultima query de la conversacion
    """
    get_messages_last_query = """
        SELECT message
        FROM messages
        WHERE conversation_id = %s AND type = 'query'
        ORDER BY id DESC
        LIMIT 1
    """
    with DBHandler() as db:
        messages = db.select(get_messages_last_query, (conversation_id,))
        if messages:
            messages = messages[0]
            return messages.get("message").get("content")

def get_option_messages(conversation_id: int):
    """
    Obtiene los mensajes enviados en una conversación
    """
    get_option_messages_query = """
        SELECT message
        FROM messages
        WHERE conversation_id = %s AND type = 'option'
        ORDER BY id DESC
        limit 1
    """
    with DBHandler() as db:
        messages = db.select(get_option_messages_query, (conversation_id,))
        if messages is None:
            return []
        messages = [item.get("message") for item in messages]
        return messages[0]