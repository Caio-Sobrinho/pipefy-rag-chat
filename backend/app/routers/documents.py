from fastapi import APIRouter, Depends

from app.core.dependencies import get_document_service
from app.models.schemas import (
    DeleteDocumentResponse,
    DocumentChunkResponse,
    DocumentResponse,
)
from app.services.document_service import DocumentService


router = APIRouter(tags=["Documents"])


@router.get("/documents", response_model=list[DocumentResponse])
async def list_documents(
    document_service: DocumentService = Depends(get_document_service),
) -> list[DocumentResponse]:
    return document_service.list_documents()


@router.get("/documents/{file_id}/chunks", response_model=list[DocumentChunkResponse])
async def list_document_chunks(
    file_id: str,
    document_service: DocumentService = Depends(get_document_service),
) -> list[DocumentChunkResponse]:
    return document_service.list_document_chunks(file_id)


@router.delete("/documents/{file_id}", response_model=DeleteDocumentResponse)
async def delete_document(
    file_id: str,
    document_service: DocumentService = Depends(get_document_service),
) -> DeleteDocumentResponse:
    document_service.delete_document(file_id)

    return DeleteDocumentResponse(
        deleted=True,
        file_id=file_id,
    )