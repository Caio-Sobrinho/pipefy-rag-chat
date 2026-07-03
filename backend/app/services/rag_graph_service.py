from typing import Optional, TypedDict

from langgraph.graph import END, START, StateGraph

from app.config import Settings
from app.models.schemas import ChatResponse, RetrievedChunkResponse, SourceResponse
from app.services.context_builder_service import ContextBuilderService
from app.services.llm_service import LLMService
from app.services.retriever_service import RetrieverService


class RagGraphState(TypedDict, total=False):
    question: str
    session_id: str
    top_k: int
    history: list[dict[str, str]]

    retrieved_chunks: list[RetrievedChunkResponse]
    context: str
    prompt: str

    llm_answer: Optional[str]
    answer: str
    sources: list[SourceResponse]


class RagGraphService:
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
        self.graph = self._build_graph()

    def _build_graph(self):
        graph = StateGraph(RagGraphState)

        graph.add_node("retriever_node", self._retriever_node)
        graph.add_node("context_builder_node", self._context_builder_node)
        graph.add_node("llm_node", self._llm_node)
        graph.add_node("response_formatter_node", self._response_formatter_node)

        graph.add_edge(START, "retriever_node")
        graph.add_edge("retriever_node", "context_builder_node")
        graph.add_edge("context_builder_node", "llm_node")
        graph.add_edge("llm_node", "response_formatter_node")
        graph.add_edge("response_formatter_node", END)

        return graph.compile()

    async def run(
        self,
        question: str,
        session_id: str,
        top_k: int,
        history: list[dict[str, str]],
    ) -> ChatResponse:
        initial_state: RagGraphState = {
            "question": question,
            "session_id": session_id,
            "top_k": top_k,
            "history": history,
        }

        final_state = await self.graph.ainvoke(initial_state)

        return ChatResponse(
            answer=final_state["answer"],
            sources=final_state.get("sources", []),
            session_id=session_id,
        )

    async def _retriever_node(self, state: RagGraphState) -> RagGraphState:
        retrieved_chunks = await self.retriever_service.retrieve(
            question=state["question"],
            top_k=state["top_k"],
        )

        return {
            "retrieved_chunks": retrieved_chunks,
        }

    async def _context_builder_node(self, state: RagGraphState) -> RagGraphState:
        retrieved_chunks = state.get("retrieved_chunks", [])

        context = self.context_builder.build_context(retrieved_chunks)
        history = self.context_builder.build_history(state.get("history", []))

        prompt = self.context_builder.build_prompt(
            question=state["question"],
            context=context,
            history=history,
        )

        sources = [
            SourceResponse(
                chunk=chunk.content,
                source=chunk.source,
                score=chunk.score,
            )
            for chunk in retrieved_chunks
        ]

        return {
            "context": context,
            "prompt": prompt,
            "sources": sources,
        }

    async def _llm_node(self, state: RagGraphState) -> RagGraphState:
        retrieved_chunks = state.get("retrieved_chunks", [])

        if not retrieved_chunks:
            return {
                "llm_answer": None,
            }

        llm_answer = await self.llm_service.generate(state["prompt"])

        return {
            "llm_answer": llm_answer,
        }

    async def _response_formatter_node(self, state: RagGraphState) -> RagGraphState:
        sources = state.get("sources", [])
        retrieved_chunks = state.get("retrieved_chunks", [])
        llm_answer = state.get("llm_answer")

        if not retrieved_chunks:
            answer = (
                "Não encontrei trechos relevantes nos documentos enviados para responder "
                "essa pergunta. Tente enviar um documento relacionado ao assunto ou reformular a pergunta."
            )

            return {
                "answer": answer,
                "sources": sources,
            }

        if llm_answer:
            return {
                "answer": llm_answer,
                "sources": sources,
            }

        answer = self._build_local_fallback_answer(
            question=state["question"],
            sources=sources,
        )

        return {
            "answer": answer,
            "sources": sources,
        }

    def _build_local_fallback_answer(
        self,
        question: str,
        sources: list[SourceResponse],
    ) -> str:
        if not sources:
            return (
                "Não encontrei fontes suficientes para responder essa pergunta "
                "com base nos documentos enviados."
            )

        best_source = sources[0]

        return (
            "O Ollama não está disponível no momento, então gerei uma resposta local "
            "com base no trecho mais relevante recuperado pelo pipeline RAG com LangGraph.\n\n"
            f"Pergunta: {question}\n\n"
            f"Trecho mais relevante encontrado em `{best_source.source}`:\n\n"
            f"{best_source.chunk[:1200]}"
        )