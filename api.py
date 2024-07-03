from controllers import bedrock_controller
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

@app.get("/ping/")
def read_root():
    return {"Ping": "Pong"}


class Message(BaseModel):
    prompt: str
    conversation_id: int

@app.post("/sendMessage/")
def read_root(message: Message):
    return bedrock_controller.send_prompt(message.prompt, message.conversation_id)

