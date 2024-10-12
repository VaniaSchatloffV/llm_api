from typing import Optional
from pydantic import BaseModel

class Metric(BaseModel):
    conversation_id: int
    calification: int
    questions: Optional[dict] = None
