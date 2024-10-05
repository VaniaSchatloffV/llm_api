from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.crons.events import delete_expired
from app.dependencies import get_settings

setings = get_settings()

@asynccontextmanager
async def lifespan(app:FastAPI):
    delete_expired()
    yield
    

app = FastAPI(lifespan=lifespan)