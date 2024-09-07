from fastapi import FastAPI

from app.routers import router

app = FastAPI(
    title="LLM interaction API",
)

@app.get("/ping/")
def read_root():
    return {"Ping": "Pong"}

app.include_router(router)