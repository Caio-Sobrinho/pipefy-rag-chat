import logging
from typing import Any

import numpy as np

from app.config import Settings
from app.core.exceptions import AppException
from app.models.schemas import RetrievedChunkResponse
from app.services.document_service import DocumentService
from app.services.embedding_service import EmbeddingService
from app.services.redis_vector_service import RedisVectorService


logger = logging.getLogger(__name__)


class RetrieverService:
    def __init__(
        self,
        settings: Settings,
        document_service: DocumentService,
        redis_vector_service: RedisVectorService,
    ):
        self.settings = settings
        self.document_service = document_service
        self.redis_vector_service = redis_vector_service
        self.embedding_service = EmbeddingService(
            model_name=settings.embedding_model,
            expected_dimension=settings.embedding_dimension,
        )

    async def retrieve(
        self,
        question: str,
        top_k: int,
    ) -> list[RetrievedChunkResponse]:
        if not question or not question.strip():
            raise AppException("Question is required.", status_code=400)

        query_embedding = self.embedding_service.embed_texts([question])[0]

        redis_available = await self.redis_vector_service.redis_service.ping()

        if redis_available:
            try:
                redis_matches = await self.redis_vector_service.similarity_search(
                    query_embedding=query_embedding,
                    top_k=top_k,
                )

                if redis_matches:
                    return [
                        RetrievedChunkResponse(
                            file_id=match["file_id"],
                            source=match["source"],
                            chunk_index=match["chunk_index"],
                            content=match["content"],
                            score=match["score"],
                            retrieval_mode="redis",
                        )
                        for match in redis_matches
                    ]
            except Exception:
                logger.exception(
                    "Redis vector search failed. Falling back to in-memory search."
                )

        return self._memory_similarity_search(
            query_embedding=query_embedding,
            top_k=top_k,
        )

    def _memory_similarity_search(
        self,
        query_embedding: list[float],
        top_k: int,
    ) -> list[RetrievedChunkResponse]:
        chunk_records = self.document_service.get_all_chunk_records()

        if not chunk_records:
            return []

        scored_chunks: list[dict[str, Any]] = []

        query_vector = np.asarray(query_embedding, dtype=np.float32)

        for chunk in chunk_records:
            embedding = chunk.get("embedding")

            if embedding is None:
                continue

            chunk_vector = np.asarray(embedding, dtype=np.float32)

            score = self._cosine_similarity(
                query_vector=query_vector,
                document_vector=chunk_vector,
            )

            scored_chunks.append(
                {
                    "file_id": chunk["file_id"],
                    "source": chunk["source"],
                    "chunk_index": chunk["chunk_index"],
                    "content": chunk["content"],
                    "score": score,
                }
            )

        scored_chunks.sort(
            key=lambda item: item["score"],
            reverse=True,
        )

        top_matches = scored_chunks[:top_k]

        return [
            RetrievedChunkResponse(
                file_id=match["file_id"],
                source=match["source"],
                chunk_index=match["chunk_index"],
                content=match["content"],
                score=match["score"],
                retrieval_mode="memory",
            )
            for match in top_matches
        ]

    def _cosine_similarity(
        self,
        query_vector: np.ndarray,
        document_vector: np.ndarray,
    ) -> float:
        query_norm = np.linalg.norm(query_vector)
        document_norm = np.linalg.norm(document_vector)

        if query_norm == 0 or document_norm == 0:
            return 0.0

        score = np.dot(query_vector, document_vector) / (
            query_norm * document_norm
        )

        return float(score)