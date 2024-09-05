from typing import Optional
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

def get_conversation_table(limit: Optional[int] = None, offset: Optional[int] = None, order_by: Optional[str] = None, order_way: Optional[str] = None):
    total = conversation_helper.count_conversations()
    if offset >= total:
        next_offset = None
    else:
        next_offset = offset + limit
        if next_offset >= total:
            next_offset = None
    return {"data" : conversation_helper.get_conversation_table(offset, limit, order_by, order_way), "total": total, "next_offset": next_offset}