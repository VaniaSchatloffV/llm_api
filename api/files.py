from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel
from helpers import file_helper
import os
from io import BytesIO

router = APIRouter()

class File(BaseModel):
    file_id: int


@router.get("/download/csv")
def download_csv(file: File):
    return StreamingResponse(file_helper.download_csv_file(file.file_id),
                             media_type="csv",
                             headers={"Content-Disposition": f"attachment; filename={os.path.basename(file_helper.get_file_csv_name(file.file_id))}"})

@router.get("/download/xlsx")
def download_xlsx(file: File):
    return StreamingResponse(
        file_helper.download_xlsx_file(file.file_id),
        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        headers={"Content-Disposition": f"attachment; filename={os.path.basename(file_helper.get_file_xlsx_name(file.file_id))}"}
    )
