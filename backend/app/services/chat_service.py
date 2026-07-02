from uuid import uuid4

from app.config import Settings
from app.models.schemas import ChatRequest, ChatResponse, SourceResponse
from app.services.context_builder_service import ContextBuilderService
from app.services.llm_service import LLMService
from app.services.retriever_service import RetrieverService


class ChatService:
    def __init__(
        self,
        settings: Settings,
        retriever_service: RetrieverService,
        llm_service: LLMService,
    ):
        self.settings = settings
        self.retriever_service = retriever_service
        self.llm_service = llm_service
        self.context_builder = ContextBuilderService()

        self.sessions: dict[str, list[dict[str, str]]] = {}

    async def answer(self, payload: ChatRequest) -> ChatResponse:
        session_id = payload.session_id or str(uuid4())

        if session_id not in self.sessions:
            self.sessions[session_id] = []

        session_messages = self.sessions[session_id]

        retrieved_chunks = await self.retriever_service.retrieve(
            question=payload.question,
            top_k=payload.top_k,
        )

        sources = [
            SourceResponse(
                chunk=chunk.content,
                source=chunk.source,
                score=chunk.score,
            )
            for chunk in retrieved_chunks
        ]

        if not retrieved_chunks:
            answer = (
                "Não encontrei trechos relevantes nos documentos enviados para responder "
                "essa pergunta. Tente enviar um documento relacionado ao assunto ou reformular a pergunta."
            )

            session_messages.append(
                {
                    "role": "user",
                    "content": payload.question,
                }
            )
            session_messages.append(
                {
                    "role": "assistant",
                    "content": answer,
                }
            )

            return ChatResponse(
                answer=answer,
                sources=sources,
                session_id=session_id,
            )

        context = self.context_builder.build_context(retrieved_chunks)
        history = self.context_builder.build_history(session_messages)

        prompt = self.context_builder.build_prompt(
            question=payload.question,
            context=context,
            history=history,
        )

        llm_answer = await self.llm_service.generate(prompt)

        if llm_answer:
            answer = llm_answer
        else:
            answer = self._build_local_fallback_answer(
                question=payload.question,
                sources=sources,
            )

        session_messages.append(
            {
                "role": "user",
                "content": payload.question,
            }
        )
        session_messages.append(
            {
                "role": "assistant",
                "content": answer,
            }
        )

        return ChatResponse(
            answer=answer,
            sources=sources,
            session_id=session_id,
        )

    def _build_local_fallback_answer(
        self,
        question: str,
        sources: list[SourceResponse],
    ) -> str:
        best_source = sources[0]

        return (
            "O Ollama não está disponível no momento, então gerei uma resposta local "
            "com base no trecho mais relevante recuperado.\n\n"
            f"Pergunta: {question}\n\n"
            f"Trecho mais relevante encontrado em `{best_source.source}`:\n\n"
            f"{best_source.chunk[:1200]}"
        )