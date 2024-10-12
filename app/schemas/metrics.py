from typing import Optional
from pydantic import BaseModel

class Metric(BaseModel):
    conversation_id: int
    calification: int
    questions: Optional[dict] = None

class MetricTable(BaseModel):
    limit: Optional[int] = 10
    offset: Optional[int] = 0
    order_by: Optional[str] = "metric_id"
    order_way: Optional[str] = "desc"