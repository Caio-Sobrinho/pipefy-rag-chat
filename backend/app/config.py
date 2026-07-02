from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Pipefy RAG Chat API"
    app_env: str = "local"
    debug: bool = True

    redis_url: str = "redis://localhost:6379"
    redis_required: bool = False
    redis_index_name: str = "idx:docs"
    redis_key_prefix: str = "doc:"

    cors_origins: str = "http://localhost:3000,http://localhost:5173"

    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    embedding_dimension: int = 384

    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.1:8b"

    chunk_size: int = 500
    chunk_overlap: int = 50
    top_k: int = 5

    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    @property
    def allowed_cors_origins(self) -> list[str]:
        return [
            origin.strip()
            for origin in self.cors_origins.split(",")
            if origin.strip()
        ]


@lru_cache
def get_settings() -> Settings:
    return Settings()