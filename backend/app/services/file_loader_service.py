from pathlib import Path

from docx import Document
from pypdf import PdfReader

from app.core.exceptions import AppException


class FileLoaderService:
    def load_text(self, file_path: str) -> str:
        path = Path(file_path)
        extension = path.suffix.lower()

        if extension == ".txt":
            return self._load_txt(path)

        if extension == ".pdf":
            return self._load_pdf(path)

        if extension == ".docx":
            return self._load_docx(path)

        raise AppException(
            "Unsupported file type. Allowed formats: PDF, TXT and DOCX.",
            status_code=400,
        )

    def _load_txt(self, path: Path) -> str:
        try:
            return path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            return path.read_text(encoding="latin-1")
        except Exception as exc:
            raise AppException("Failed to read TXT file.", status_code=500) from exc

    def _load_pdf(self, path: Path) -> str:
        try:
            reader = PdfReader(str(path))
            pages_text: list[str] = []

            for page in reader.pages:
                text = page.extract_text() or ""
                if text.strip():
                    pages_text.append(text)

            return "\n\n".join(pages_text)
        except Exception as exc:
            raise AppException("Failed to read PDF file.", status_code=500) from exc

    def _load_docx(self, path: Path) -> str:
        try:
            document = Document(str(path))
            paragraphs = [
                paragraph.text
                for paragraph in document.paragraphs
                if paragraph.text.strip()
            ]

            return "\n".join(paragraphs)
        except Exception as exc:
            raise AppException("Failed to read DOCX file.", status_code=500) from exc