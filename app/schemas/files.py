from typing import Optional
from pydantic import BaseModel

class File(BaseModel):
    file_id: int
