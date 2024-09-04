from helpers import conversation_helper

def get_conversation(user_id: int):
    """
    Obtiene conversaciones de un usuario
    """
    return conversation_helper.get_conversations(user_id)

def get_conversation_messages(conversation_id: int):
    """
    Obtiene mensajes de un usuario
    """
    return conversation_helper.get_messages(conversation_id)

def change_conversation_name(conversation_id: int, name: str):
    status = conversation_helper.change_conversation_name(conversation_id, name)
    return {"changed": status != 0}
