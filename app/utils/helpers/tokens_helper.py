import json
from typing import Optional

from app.models.tokens import TokenObject
from app.models.chat import ConversationObject
from app.crud.DBORMHandler import DB_ORM_Handler

def create_tokens_for_conversation(conversation_id:int):
    with DB_ORM_Handler() as db:
        token = TokenObject()
        token.conversation_id = conversation_id
        db.saveObject(token)

def set_tokens(conversation_id:int, input_tokens_used_conversation:int, output_tokens_used_conversation:int):
    with DB_ORM_Handler() as db:
        db.updateObjects(
            TokenObject,
            TokenObject.conversation_id == conversation_id,
            input_tokens_used = input_tokens_used_conversation,
            output_tokens_used = output_tokens_used_conversation
        )
    return

def get_tokens(conversation_id:int):
    with DB_ORM_Handler() as db:
        tokens_usados_conversacion = db.getObjects(
            TokenObject,
            TokenObject.conversation_id == conversation_id,
            columns=[TokenObject.input_tokens_used, TokenObject.output_tokens_used]
        )
    if tokens_usados_conversacion:
        input_and_output_tokens = tokens_usados_conversacion.pop()
        return input_and_output_tokens.get("input_tokens_used"), input_and_output_tokens.get("output_tokens_used")
    return 