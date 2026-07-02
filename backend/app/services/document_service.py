import shutil
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile

from app.config import Settings
from app.core.exceptions import AppException
from app.models.schemas import (
    DocumentChunkResponse,
    DocumentResponse,
    UploadResponse,
)
from app.services.file_loader_service import FileLoaderService
from app.services.text_splitter_service import TextSplitterService


class DocumentService:
    allowed_extensions = {".pdf", ".txt", ".docx"}

    def __init__(
        self,
        settings: Settings,
        upload_dir: str = "storage/uploads",
    ):
        self.settings = settings
        self.upload_dir = Path(upload_dir)
        self.upload_dir.mkdir(parents=True, exist_ok=True)

        self.file_loader = FileLoaderService()
        self.text_splitter = TextSplitterService()

        # Armazenamento temporário em memória.
        # No Bloco 4, os chunks serão indexados no Redis.
        self.documents: dict[str, dict] = {}
        self.chunks: dict[str, list[dict]] = {}

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

        text = self.file_loader.load_text(str(stored_path))

        chunks = self.text_splitter.split_text(
            text=text,
            chunk_size=self.settings.chunk_size,
            chunk_overlap=self.settings.chunk_overlap,
        )

        uploaded_at = datetime.now(timezone.utc)

        self.documents[file_id] = {
            "file_id": file_id,
            "name": original_name,
            "uploaded_at": uploaded_at,
            "chunks": len(chunks),
            "status": "indexed",
            "path": str(stored_path),
        }

        self.chunks[file_id] = [
            {
                "file_id": file_id,
                "source": original_name,
                "chunk_index": index,
                "content": chunk,
                "uploaded_at": uploaded_at,
            }
            for index, chunk in enumerate(chunks)
        ]

        return UploadResponse(
            file_id=file_id,
            name=original_name,
            chunks_indexed=len(chunks),
            status="indexed",
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

    def list_document_chunks(self, file_id: str) -> list[DocumentChunkResponse]:
        if file_id not in self.documents:
            raise AppException("Document not found.", status_code=404)

        return [
            DocumentChunkResponse(
                file_id=chunk["file_id"],
                source=chunk["source"],
                chunk_index=chunk["chunk_index"],
                content=chunk["content"],
            )
            for chunk in self.chunks.get(file_id, [])
        ]

    def delete_document(self, file_id: str) -> bool:
        document = self.documents.pop(file_id, None)

        if document is None:
            raise AppException("Document not found.", status_code=404)

        self.chunks.pop(file_id, None)

        path = Path(document["path"])

        if path.exists():
            path.unlink()

        return True