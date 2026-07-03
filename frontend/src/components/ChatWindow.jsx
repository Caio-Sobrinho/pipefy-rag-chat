import { useState } from "react";
import { sendChatMessage } from "../api/client";
import { SourceList } from "./SourceList";

export function ChatWindow({ activeSession, onMessageSent }) {
  const [question, setQuestion] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleSubmit(event) {
    event.preventDefault();

    if (!question.trim()) return;

    const userMessage = {
      role: "user",
      content: question,
    };

    onMessageSent(activeSession.id, userMessage);

    try {
      setError("");
      setIsLoading(true);

      const response = await sendChatMessage({
        question,
        sessionId: activeSession.id,
        topK: 3,
      });

      const assistantMessage = {
        role: "assistant",
        content: response.answer,
        sources: response.sources,
      };

      onMessageSent(activeSession.id, assistantMessage);
      setQuestion("");
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <section className="card chat-card">
      <div className="chat-header">
        <h2>{activeSession.name}</h2>
        <p className="muted">Sessão: {activeSession.id}</p>
      </div>

      <div className="messages">
        {activeSession.messages.length === 0 ? (
          <p className="muted">
            Faça uma pergunta sobre os documentos enviados.
          </p>
        ) : (
          activeSession.messages.map((message, index) => (
            <div
              key={index}
              className={`message ${
                message.role === "user" ? "message-user" : "message-assistant"
              }`}
            >
              <strong>{message.role === "user" ? "Você" : "Assistente"}</strong>
              <p>{message.content}</p>

              {message.role === "assistant" && (
                <SourceList sources={message.sources} />
              )}
            </div>
          ))
        )}

        {isLoading && <p className="muted">Gerando resposta...</p>}
      </div>

      <form onSubmit={handleSubmit} className="chat-form">
        <input
          value={question}
          onChange={(event) => setQuestion(event.target.value)}
          placeholder="Pergunte algo sobre os documentos..."
        />

        <button type="submit" disabled={isLoading}>
          Enviar
        </button>
      </form>

      {error && <p className="error">{error}</p>}
    </section>
  );
}