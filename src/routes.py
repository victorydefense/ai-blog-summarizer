from fastapi import APIRouter
from src import services
from src.models import SummarizeRequest, SummarizeResponse

router = APIRouter()

@router.post("/summarize", response_model=SummarizeResponse)
async def summarize_blog(request: SummarizeRequest):
    summary = services.summarize_blog(request.url)
    return summary