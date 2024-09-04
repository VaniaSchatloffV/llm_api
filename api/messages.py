from controllers import bedrock_controller, conversation_controller
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

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


@router.post("/sendMessage/")
def send_prompt(message: Message):
    return bedrock_controller.send_prompt_and_process(message.prompt, message.conversation_id, message.user_id)


@router.get("/getConversations/")
def get_conversation(conversation: Conversations):
    return conversation_controller.get_conversation(conversation.user_id)


@router.get("/getConversationMessages/")
def get_conversation(conversation: Conversation):
    return conversation_controller.get_conversation_messages(conversation.conversation_id)

@router.post("/changeConversationName/")
def change_conversation_name(conversation: ConversationName):
    return conversation_controller.change_conversation_name(conversation.conversation_id, conversation.name)

