from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from app.utils.helpers import file_helper
from app.utils.auth import TokenData, verify_token
import os

from app.schemas.files import File

router = APIRouter()

@router.get("/download/")
def download(file: File, token_data: TokenData = Depends(verify_token)):
    return StreamingResponse(
        file_helper.download_file(file.file_id),
        #media_type="csv",
        headers={"Content-Disposition": f"attachment; filename={os.path.basename(file_helper.get_file_path(file.file_id))}"}
    )


@router.get("/check/")
def download_xlsx(file: File, token_data: TokenData = Depends(verify_token)):
    return file_helper.file_exists(file_id=file.file_id)
