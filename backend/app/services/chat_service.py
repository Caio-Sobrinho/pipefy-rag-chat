from uuid import uuid4

from app.models.schemas import ChatRequest, ChatResponse


class ChatService:
    def __init__(self):
        self.sessions: dict[str, list[dict[str, str]]] = {}

    def answer(self, payload: ChatRequest) -> ChatResponse:
        session_id = payload.session_id or str(uuid4())

        if session_id not in self.sessions:
            self.sessions[session_id] = []

        self.sessions[session_id].append(
            {
                "role": "user",
                "content": payload.question,
            }
        )

        answer = (
            "Resposta mockada do Bloco 2. "
            "A API já recebeu sua pergunta e manteve a sessão ativa. "
            "No próximo bloco, essa resposta será gerada usando RAG com documentos indexados."
        )

        self.sessions[session_id].append(
            {
                "role": "assistant",
                "content": answer,
            }
        )

        return ChatResponse(
            answer=answer,
            sources=[],
            session_id=session_id,
        )