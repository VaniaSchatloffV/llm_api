import os
import uvicorn
from fastapi import FastAPI
from api.messages import router as messages_router
from api.files import router as files_router

app = FastAPI(
    title="LLM interaction API",

)

@app.get("/ping/")
def read_root():
    return {"Ping": "Pong"}


app.include_router(messages_router)
app.include_router(files_router)

if __name__ == "__main__":
    host = host=os.getenv("HOST")
    port = int(os.getenv("PORT"))
    if os.getenv("ENVIRONMENT") == 'dev':
        uvicorn.run("app:app", host=host, port=port, reload=True)
    elif os.getenv("ENVIRONMENT") == 'prod':
        uvicorn.run("app:app", host=host, port=port)