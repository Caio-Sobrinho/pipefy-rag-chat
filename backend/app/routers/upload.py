from fastapi import APIRouter, Depends, File, UploadFile

from app.core.dependencies import get_document_service
from app.models.schemas import UploadResponse
from app.services.document_service import DocumentService


router = APIRouter(tags=["Upload"])


@router.post("/upload", response_model=UploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    document_service: DocumentService = Depends(get_document_service),
) -> UploadResponse:
    return await document_service.save_uploaded_file(file)