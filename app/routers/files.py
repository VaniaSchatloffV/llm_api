from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from app.utils.helpers import file_helper
import os

from app.schemas.files import File

router = APIRouter()

@router.get("/download/csv/")
def download_csv(file: File):
    return StreamingResponse(file_helper.download_csv_file(file.file_id),
                             media_type="csv",
                             headers={"Content-Disposition": f"attachment; filename={os.path.basename(file_helper.get_file_csv_name(file.file_id))}"})

@router.get("/download/xlsx/")
def download_xlsx(file: File):
    return StreamingResponse(
        file_helper.download_xlsx_file(file.file_id),
        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        headers={"Content-Disposition": f"attachment; filename={os.path.basename(file_helper.get_file_xlsx_name(file.file_id))}"}
    )



@router.get("/check/")
def download_xlsx(file: File):
    return file_helper.file_exists(file_id=file.file_id, file_type=file.file_type)
