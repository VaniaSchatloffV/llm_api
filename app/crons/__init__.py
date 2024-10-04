from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.crons.events import delete_expired

@asynccontextmanager
async def lifespan(app:FastAPI):
    delete_expired()
    yield