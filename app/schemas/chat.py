from typing import Optional
from pydantic import BaseModel

class Message(BaseModel):
    prompt: str
    conversation_id: int
    user_id: int

class Conversations(BaseModel):
    user_id: int

class Conversation(BaseModel):
    conversation_id: int

class ConversationName(BaseModel):
    conversation_id: int
    name: str

class ConversationTable(BaseModel):
    limit: Optional[int] = 10
    offset: Optional[int] = 0
    order_by: Optional[str] = "conversation_id"
    order_way: Optional[str] = "desc"
