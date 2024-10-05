from fastapi import FastAPI
from app.routers import router
from app.crons import lifespan


app = FastAPI(
    title="LLM interaction API",
    lifespan=lifespan
)

@app.get("/ping/")
def read_root():
    return {"Ping": "Pong"}

app.include_router(router)