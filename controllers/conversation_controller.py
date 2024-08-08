from handlers.DBHandler import DBHandler
from helpers import conversation_helper

def get_conversation(user_id: int):
    """
    Obtiene conversaciones de un usuario
    """
    get_conversations_query = """
        SELECT id, name, created_at
        FROM conversations
        WHERE user_id = %s
        ORDER BY id
    """
    with DBHandler() as db:
        conversations = db.select(get_conversations_query, (user_id,))
        if conversations is None:
            return []
        return conversations

def get_conversation_messages(conversation_id: int):
    return conversation_helper.get_messages(conversation_id)