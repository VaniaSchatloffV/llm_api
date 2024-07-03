conversations = {}

def check_conversation(conversation_id: int):
    if conversation_id not in conversations.keys():
        conversations[conversation_id] = []
        return False
    return True



def add_user_message(conversation_id: int, content: str):
    conversations[conversation_id].append({"role": "user", "content": content})

def add_assistant_message(conversation_id: int, content: list):
    conversations[conversation_id].append({"role": "assistant", "content": content})

def get_conversation(conversation_id: int):
    return conversations.get(conversation_id)