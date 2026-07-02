from app.core.exceptions import AppException


class TextSplitterService:
    def split_text(
        self,
        text: str,
        chunk_size: int,
        chunk_overlap: int,
    ) -> list[str]:
        if not text or not text.strip():
            raise AppException(
                "The uploaded file does not contain readable text.",
                status_code=400,
            )

        if chunk_size <= 0:
            raise AppException("chunk_size must be greater than zero.", status_code=500)

        if chunk_overlap < 0:
            raise AppException("chunk_overlap cannot be negative.", status_code=500)

        if chunk_overlap >= chunk_size:
            raise AppException(
                "chunk_overlap must be smaller than chunk_size.",
                status_code=500,
            )

        words = text.split()
        chunks: list[str] = []

        start = 0

        while start < len(words):
            end = start + chunk_size
            chunk_words = words[start:end]
            chunk = " ".join(chunk_words).strip()

            if chunk:
                chunks.append(chunk)

            start += chunk_size - chunk_overlap

        return chunks