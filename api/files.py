from fastapi import APIRouter
from fastapi.responses import FileResponse
from pydantic import BaseModel
from helpers import file_helper

router = APIRouter()

class File(BaseModel):
    file_id: int


@router.get("/download/csv")
def download_csv(file: File):
    return FileResponse(file_helper.get_file_csv_name(file.file_id), media_type="csv")

@router.get("/download/xlsx")
def download_csv(file: File):
    return FileResponse(file_helper.get_file_xlsx_name(file.file_id), media_type="xlsx")
