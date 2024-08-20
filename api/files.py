from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel
from helpers import file_helper
import os
from io import BytesIO

router = APIRouter()

class File(BaseModel):
    file_id: int


@router.get("/download/{file_id}/csv")
def download_csv(file_id: str):
    return StreamingResponse(file_helper.download_csv_file(file_id),
                             media_type="csv",
                             headers={"Content-Disposition": f"attachment; filename={os.path.basename(file_helper.get_file_csv_name(file_id))}"})

@router.get("/download/{file_id}/xlsx")
def download_xlsx(file_id: int):
    return StreamingResponse(
        file_helper.download_xlsx_file(file_id),
        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        headers={"Content-Disposition": f"attachment; filename={os.path.basename(file_helper.get_file_xlsx_name(file_id))}"}
    )
