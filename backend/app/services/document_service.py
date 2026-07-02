import shutil
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile

from app.core.exceptions import AppException
from app.models.schemas import DocumentResponse, UploadResponse


class DocumentService:
    allowed_extensions = {".pdf", ".txt", ".docx"}

    def __init__(self, upload_dir: str = "storage/uploads"):
        self.upload_dir = Path(upload_dir)
        self.upload_dir.mkdir(parents=True, exist_ok=True)

        # Banco temporário em memória.
        # No próximo bloco, isso será substituído/espelhado no Redis.
        self.documents: dict[str, dict] = {}

    async def save_uploaded_file(self, file: UploadFile) -> UploadResponse:
        if not file.filename:
            raise AppException("File name is required.", status_code=400)

        original_name = Path(file.filename).name
        extension = Path(original_name).suffix.lower()

        if extension not in self.allowed_extensions:
            raise AppException(
                "Unsupported file type. Allowed formats: PDF, TXT and DOCX.",
                status_code=400,
            )

        file_id = str(uuid4())
        stored_name = f"{file_id}{extension}"
        stored_path = self.upload_dir / stored_name

        try:
            with stored_path.open("wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
        except Exception as exc:
            raise AppException("Failed to save uploaded file.", status_code=500) from exc
        finally:
            await file.close()

        uploaded_at = datetime.now(timezone.utc)

        self.documents[file_id] = {
            "file_id": file_id,
            "name": original_name,
            "uploaded_at": uploaded_at,
            "chunks": 0,
            "status": "uploaded",
            "path": str(stored_path),
        }

        return UploadResponse(
            file_id=file_id,
            name=original_name,
            chunks_indexed=0,
            status="uploaded",
        )

    def list_documents(self) -> list[DocumentResponse]:
        return [
            DocumentResponse(
                file_id=document["file_id"],
                name=document["name"],
                uploaded_at=document["uploaded_at"],
                chunks=document["chunks"],
                status=document["status"],
            )
            for document in self.documents.values()
        ]

    def delete_document(self, file_id: str) -> bool:
        document = self.documents.pop(file_id, None)

        if document is None:
            raise AppException("Document not found.", status_code=404)

        path = Path(document["path"])

        if path.exists():
            path.unlink()

        return True