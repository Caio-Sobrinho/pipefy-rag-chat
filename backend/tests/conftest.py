import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.embedding_service import EmbeddingService
from app.services.llm_service import LLMService
from app.services.redis_vector_service import RedisVectorService


def fake_embedding_vector() -> list[float]:
    return [1.0] + [0.0] * 383


@pytest.fixture(autouse=True)
def mock_external_services(monkeypatch):
    def fake_embed_texts(self, texts):
        clean_texts = [text for text in texts if text and text.strip()]
        return [fake_embedding_vector() for _ in clean_texts]

    async def fake_index_chunks(self, chunks):
        return 0

    async def fake_delete_document_vectors(self, file_id):
        return 0

    async def fake_llm_generate(self, prompt):
        return "Resposta gerada pelo mock do LLM com base no contexto recuperado."

    monkeypatch.setattr(EmbeddingService, "embed_texts", fake_embed_texts)
    monkeypatch.setattr(RedisVectorService, "index_chunks", fake_index_chunks)
    monkeypatch.setattr(
        RedisVectorService,
        "delete_document_vectors",
        fake_delete_document_vectors,
    )
    monkeypatch.setattr(LLMService, "generate", fake_llm_generate)


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def sample_txt_file():
    content = (
        "A Pipefy é uma plataforma de automação de processos. "
        "O time de Data e AI trabalha com inteligência artificial, dados, "
        "RAG, modelos de linguagem e busca semântica."
    )

    return {
        "file": (
            "sample.txt",
            content.encode("utf-8"),
            "text/plain",
        )
    }