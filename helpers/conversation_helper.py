import json
from datetime import datetime
from handlers.DBHandler import DBHandler


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

def insert_message(conversation_id: int, role: str, content):
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
        INSERT INTO messages (conversation_id, message)
        VALUES (%s, %s)
    """
    with DBHandler() as db:
        db.execute(insert_new_message, (conversation_id, message_json))

def get_messages(conversation_id: int):
    """
    Obtiene los mensajes enviados en una conversación
    """
    get_messages_query = """
        SELECT message
        FROM messages
        WHERE conversation_id = %s
        ORDER BY id
    """
    with DBHandler() as db:
        messages = db.select(get_messages_query, (conversation_id,))
        messages = [item[0] for item in messages]
        return messages