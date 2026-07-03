from uuid import uuid4

from app.models.schemas import ChatRequest, ChatResponse
from app.services.rag_graph_service import RagGraphService


class ChatService:
    def __init__(
        self,
        rag_graph_service: RagGraphService,
    ):
        self.rag_graph_service = rag_graph_service
        self.sessions: dict[str, list[dict[str, str]]] = {}

    async def answer(self, payload: ChatRequest) -> ChatResponse:
        session_id = payload.session_id or str(uuid4())

        if session_id not in self.sessions:
            self.sessions[session_id] = []

        session_messages = self.sessions[session_id]

        response = await self.rag_graph_service.run(
            question=payload.question,
            session_id=session_id,
            top_k=payload.top_k,
            history=session_messages,
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
                "content": response.answer,
            }
        )

        return response