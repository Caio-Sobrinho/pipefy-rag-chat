from fastapi import APIRouter, Depends

from app.core.dependencies import get_retriever_service
from app.models.schemas import SearchRequest, SearchResponse
from app.services.retriever_service import RetrieverService


router = APIRouter(tags=["Search"])


@router.post("/search", response_model=SearchResponse)
async def semantic_search(
    payload: SearchRequest,
    retriever_service: RetrieverService = Depends(get_retriever_service),
) -> SearchResponse:
    matches = await retriever_service.retrieve(
        question=payload.question,
        top_k=payload.top_k,
    )

    return SearchResponse(
        question=payload.question,
        top_k=payload.top_k,
        matches=matches,
    )