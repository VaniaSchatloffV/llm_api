from typing import Optional
from controllers import bedrock_controller, conversation_controller
from fastapi import FastAPI
from api.messages import router as messages_router

app = FastAPI()

@app.get("/ping/")
def read_root():
    return {"Ping": "Pong"}


app.include_router(messages_router)