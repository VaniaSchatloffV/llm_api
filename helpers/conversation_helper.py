from datetime import datetime
conversations = {}

def check_conversation(conversation_id: int):
    if conversation_id not in conversations.keys():
        now = datetime.now()
        conversations[conversation_id] = {"created_at": now.strftime("%Y-%m-%d %H:%M:%S"), "conversation": []}
        return False
    return True



def add_user_message(conversation_id: int, content: str):
    conversations[conversation_id]["conversation"].append({"role": "user", "content": content})

def add_assistant_message(conversation_id: int, content: list):
    conversations[conversation_id]["conversation"].append({"role": "assistant", "content": content})

def get_conversation(conversation_id: int):
    return conversations.get(conversation_id).get("conversation")