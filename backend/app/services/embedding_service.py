from typing import Iterable

import numpy as np
from sentence_transformers import SentenceTransformer

from app.core.exceptions import AppException


class EmbeddingService:
    def __init__(self, model_name: str, expected_dimension: int):
        self.model_name = model_name
        self.expected_dimension = expected_dimension
        self._model: SentenceTransformer | None = None

    @property
    def model(self) -> SentenceTransformer:
        if self._model is None:
            self._model = SentenceTransformer(self.model_name)

        return self._model

    def embed_texts(self, texts: Iterable[str]) -> list[list[float]]:
        clean_texts = [text.strip() for text in texts if text and text.strip()]

        if not clean_texts:
            raise AppException(
                "No valid text chunks found to generate embeddings.",
                status_code=400,
            )

        try:
            embeddings = self.model.encode(
                clean_texts,
                normalize_embeddings=True,
                convert_to_numpy=True,
                show_progress_bar=False,
            )
        except Exception as exc:
            raise AppException(
                "Failed to generate embeddings.",
                status_code=500,
            ) from exc

        embeddings = np.asarray(embeddings, dtype=np.float32)

        if embeddings.ndim != 2:
            raise AppException(
                "Invalid embedding output shape.",
                status_code=500,
            )

        actual_dimension = int(embeddings.shape[1])

        if actual_dimension != self.expected_dimension:
            raise AppException(
                (
                    f"Embedding dimension mismatch. "
                    f"Expected {self.expected_dimension}, got {actual_dimension}."
                ),
                status_code=500,
            )

        return embeddings.tolist()