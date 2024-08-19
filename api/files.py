from fastapi import APIRouter
from fastapi.responses import FileResponse
from pydantic import BaseModel
from helpers import file_helper

router = APIRouter()

class File(BaseModel):
    file_id: int


@router.get("/download/{file_id}/csv")
def download_csv(file_id):
    return FileResponse(file_helper.get_file_csv_name(file_id), media_type="csv")

@router.get("/download/{file_id}/xlsx")
def download_csv(file_id):
    return FileResponse(file_helper.get_file_xlsx_name(file_id), media_type="xlsx")
