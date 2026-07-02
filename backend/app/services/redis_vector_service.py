import logging
from datetime import datetime
from typing import Any

import numpy as np
from redis.commands.search.field import NumericField, TagField, TextField, VectorField
from redis.commands.search.index_definition import IndexDefinition, IndexType
from redis.commands.search.query import Query
from redis.exceptions import RedisError, ResponseError

from app.config import Settings
from app.core.exceptions import AppException
from app.services.redis_service import RedisService


logger = logging.getLogger(__name__)


class RedisVectorService:
    def __init__(self, redis_service: RedisService, settings: Settings):
        self.redis_service = redis_service
        self.client = redis_service.client
        self.settings = settings
        self.index_name = settings.redis_index_name
        self.key_prefix = settings.redis_key_prefix

    async def ensure_index(self) -> bool:
        try:
            await self.client.ft(self.index_name).info()
            return True
        except ResponseError:
            return await self._create_index()
        except RedisError:
            logger.warning("Redis is not available. Vector index was not checked.")
            return False

    async def _create_index(self) -> bool:
        schema = (
            TagField("file_id"),
            TextField("source"),
            NumericField("chunk_index"),
            TextField("content"),
            TextField("uploaded_at"),
            VectorField(
                "embedding",
                "HNSW",
                {
                    "TYPE": "FLOAT32",
                    "DIM": self.settings.embedding_dimension,
                    "DISTANCE_METRIC": "COSINE",
                    "INITIAL_CAP": 1000,
                    "M": 16,
                    "EF_CONSTRUCTION": 200,
                },
            ),
        )

        definition = IndexDefinition(
            prefix=[self.key_prefix],
            index_type=IndexType.HASH,
        )

        try:
            await self.client.ft(self.index_name).create_index(
                fields=schema,
                definition=definition,
            )
            logger.info("Redis vector index created: %s", self.index_name)
            return True
        except ResponseError as exc:
            if "Index already exists" in str(exc):
                return True

            logger.exception("Failed to create Redis vector index.")
            return False
        except RedisError:
            logger.exception("Redis is not available. Vector index was not created.")
            return False

    async def index_chunks(self, chunks: list[dict[str, Any]]) -> int:
        if not chunks:
            return 0

        index_ready = await self.ensure_index()

        if not index_ready:
            return 0

        try:
            async with self.client.pipeline(transaction=False) as pipe:
                for chunk in chunks:
                    key = self._build_chunk_key(
                        file_id=chunk["file_id"],
                        chunk_index=chunk["chunk_index"],
                    )

                    uploaded_at = chunk.get("uploaded_at")

                    if isinstance(uploaded_at, datetime):
                        uploaded_at = uploaded_at.isoformat()

                    pipe.hset(
                        key,
                        mapping={
                            "file_id": chunk["file_id"],
                            "source": chunk["source"],
                            "chunk_index": int(chunk["chunk_index"]),
                            "content": chunk["content"],
                            "uploaded_at": uploaded_at or "",
                            "embedding": self._embedding_to_bytes(chunk["embedding"]),
                        },
                    )

                await pipe.execute()

            return len(chunks)
        except RedisError:
            logger.exception("Failed to index chunks in Redis.")
            return 0

    async def delete_document_vectors(self, file_id: str) -> int:
        deleted_count = 0
        cursor = 0
        pattern = f"{self.key_prefix}{file_id}:chunk:*"

        try:
            while True:
                cursor, keys = await self.client.scan(
                    cursor=cursor,
                    match=pattern,
                    count=100,
                )

                if keys:
                    deleted_count += await self.client.delete(*keys)

                if cursor == 0:
                    break

            return deleted_count
        except RedisError:
            logger.warning("Failed to delete document vectors from Redis.")
            return 0

    async def similarity_search(
        self,
        query_embedding: list[float],
        top_k: int,
    ) -> list[dict[str, Any]]:
        await self.ensure_index()

        query_vector = self._embedding_to_bytes(query_embedding)

        redis_query = (
            Query(f"(*)=>[KNN {top_k} @embedding $query_vector AS vector_score]")
            .sort_by("vector_score")
            .return_fields(
                "file_id",
                "source",
                "chunk_index",
                "content",
                "uploaded_at",
                "vector_score",
            )
            .dialect(2)
        )

        try:
            result = await self.client.ft(self.index_name).search(
                redis_query,
                query_params={"query_vector": query_vector},
            )
        except RedisError as exc:
            raise AppException(
                "Failed to perform vector search in Redis.",
                status_code=500,
            ) from exc

        matches: list[dict[str, Any]] = []

        for document in result.docs:
            distance = float(document.vector_score)
            similarity = max(0.0, 1.0 - distance)

            matches.append(
                {
                    "file_id": document.file_id,
                    "source": document.source,
                    "chunk_index": int(document.chunk_index),
                    "content": document.content,
                    "uploaded_at": document.uploaded_at,
                    "distance": distance,
                    "score": similarity,
                }
            )

        return matches

    def _build_chunk_key(self, file_id: str, chunk_index: int) -> str:
        return f"{self.key_prefix}{file_id}:chunk:{chunk_index}"

    def _embedding_to_bytes(self, embedding: list[float]) -> bytes:
        array = np.array(embedding, dtype=np.float32)

        if array.shape[0] != self.settings.embedding_dimension:
            raise AppException(
                (
                    "Invalid embedding dimension for Redis indexing. "
                    f"Expected {self.settings.embedding_dimension}, got {array.shape[0]}."
                ),
                status_code=500,
            )

        return array.tobytes()