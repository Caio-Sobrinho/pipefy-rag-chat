from app.models.schemas import RetrievedChunkResponse


class ContextBuilderService:
    def build_context(self, chunks: list[RetrievedChunkResponse]) -> str:
        if not chunks:
            return ""

        context_parts: list[str] = []

        for index, chunk in enumerate(chunks, start=1):
            context_parts.append(
                "\n".join(
                    [
                        f"[Fonte {index}]",
                        f"Arquivo: {chunk.source}",
                        f"Chunk: {chunk.chunk_index}",
                        f"Score: {chunk.score:.4f}",
                        "Conteúdo:",
                        chunk.content,
                    ]
                )
            )

        return "\n\n---\n\n".join(context_parts)

    def build_history(self, messages: list[dict[str, str]], limit: int = 6) -> str:
        if not messages:
            return ""

        recent_messages = messages[-limit:]

        history_lines: list[str] = []

        for message in recent_messages:
            role = "Usuário" if message["role"] == "user" else "Assistente"
            history_lines.append(f"{role}: {message['content']}")

        return "\n".join(history_lines)

    def build_prompt(
        self,
        question: str,
        context: str,
        history: str,
    ) -> str:
        return f"""
Você é um assistente especializado em responder perguntas com base em documentos enviados pelo usuário.

Regras obrigatórias:
1. Responda apenas com base no contexto fornecido.
2. Se a resposta não estiver no contexto, diga claramente que não encontrou essa informação nos documentos.
3. Não invente dados, nomes, datas ou conclusões.
4. Responda em português do Brasil.
5. Seja objetivo, mas explique o suficiente para o usuário entender.
6. Quando útil, mencione de qual documento veio a informação.

Histórico recente da conversa:
{history if history else "Sem histórico anterior."}

Contexto recuperado dos documentos:
{context if context else "Nenhum contexto recuperado."}

Pergunta do usuário:
{question}

Resposta:
""".strip()