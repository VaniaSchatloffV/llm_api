from fastapi import APIRouter

from .chat import router as chat_router
from .files import router as files_router

router = APIRouter()

router.include_router(chat_router, prefix="/chat", tags=["chat"])
router.include_router(files_router, prefix="/files", tags=["files"])