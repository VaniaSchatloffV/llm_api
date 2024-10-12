from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from app.utils.helpers import metrics_helper
from app.utils.auth import TokenData, verify_token
import os

from app.schemas.metrics import Metric, MetricTable

router = APIRouter()

@router.post("/send/")
def download(metric: Metric, token_data: TokenData = Depends(verify_token)):
    calification = metric.calification
    questions = metric.questions
    conversation_id = metric.conversation_id
    metrics_helper.upload_metric(conversation_id, questions, calification)

@router.get("/getTable/")
def get_metric_table(metricTable: MetricTable):
    return metrics_helper.get_metric_table(limit=metricTable.limit, offset=metricTable.offset, order_by=metricTable.order_by, order_way=metricTable.order_way)