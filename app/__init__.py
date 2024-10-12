from fastapi import FastAPI, Depends

from app.routers import router
from app.crons import lifespan
from app.utils.auth import TokenData, verify_token

app = FastAPI(
    title="LLM interaction API",
    lifespan=lifespan
)

@app.get("/ping/")
def read_root(token_data: TokenData = Depends(verify_token)):
    return {"Ping": "Pong"}

app.include_router(router)