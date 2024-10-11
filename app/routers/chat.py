from app.utils import bedrock_controller
from app.utils import conversation_controller
from fastapi import APIRouter, Depends
from app.schemas.chat import Message, Conversation, Conversations, ConversationTable, ConversationName
from app.utils.auth import TokenData, verify_token

router = APIRouter()

@router.post("/sendMessage/")
def send_prompt(message: Message, token_data: TokenData = Depends(verify_token)):
    return bedrock_controller.send_prompt_and_process(message.prompt, message.conversation_id, message.user_id)


@router.get("/getConversations/")
def get_conversation(conversation: Conversations, token_data: TokenData = Depends(verify_token)):
    return conversation_controller.get_conversation(conversation.user_id)


@router.get("/getConversationMessages/")
def get_conversation(conversation: Conversation, token_data: TokenData = Depends(verify_token)):
    return conversation_controller.get_conversation_messages(conversation.conversation_id)

@router.post("/changeConversationName/")
def change_conversation_name(conversation: ConversationName, token_data: TokenData = Depends(verify_token)):
    return conversation_controller.change_conversation_name(conversation.conversation_id, conversation.name)

@router.get("/getConversationTable/")
def get_conversation_table(conversation: ConversationTable, token_data: TokenData = Depends(verify_token)):
    return conversation_controller.get_conversation_table(conversation.limit, conversation.offset, conversation.order_by, conversation.order_way)