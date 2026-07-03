import { useEffect, useMemo, useState } from "react";
import { getHealth, listDocuments } from "./api/client";
import { ChatWindow } from "./components/ChatWindow";
import { DocumentList } from "./components/DocumentList";
import { FileUpload } from "./components/FileUpload";
import { SessionSidebar } from "./components/SessionSidebar";
import "./styles.css";

function createSession(index = 1) {
  return {
    id: crypto.randomUUID(),
    name: `Sessão ${index}`,
    messages: [],
  };
}

const initialSession = createSession(1);

export default function App() {
  const [health, setHealth] = useState(null);
  const [documents, setDocuments] = useState([]);
  const [sessions, setSessions] = useState([initialSession]);
  const [activeSessionId, setActiveSessionId] = useState(initialSession.id);
  const [error, setError] = useState("");

  const activeSession = useMemo(() => {
    return (
      sessions.find((session) => session.id === activeSessionId) || sessions[0]
    );
  }, [sessions, activeSessionId]);

  useEffect(() => {
    async function loadInitialData() {
      try {
        const [healthResponse, documentsResponse] = await Promise.all([
          getHealth(),
          listDocuments(),
        ]);

        setHealth(healthResponse);
        setDocuments(documentsResponse);
      } catch (err) {
        setError(err.message);
      }
    }

    loadInitialData();
  }, []);

  function handleUploaded(uploadResponse) {
    setDocuments((currentDocuments) => [
      ...currentDocuments,
      {
        file_id: uploadResponse.file_id,
        name: uploadResponse.name,
        chunks: uploadResponse.chunks_indexed,
        status: uploadResponse.status,
        uploaded_at: new Date().toISOString(),
      },
    ]);
  }

  function handleDeleted(fileId) {
    setDocuments((currentDocuments) =>
      currentDocuments.filter((document) => document.file_id !== fileId)
    );
  }

  function handleCreateSession() {
    const newSession = createSession(sessions.length + 1);

    setSessions((currentSessions) => [...currentSessions, newSession]);
    setActiveSessionId(newSession.id);
  }

  function handleMessageSent(sessionId, message) {
    setSessions((currentSessions) =>
      currentSessions.map((session) => {
        if (session.id !== sessionId) {
          return session;
        }

        return {
          ...session,
          messages: [...session.messages, message],
        };
      })
    );
  }

  if (!activeSession) {
    return null;
  }

  return (
    <div className="app-layout">
      <SessionSidebar
        sessions={sessions}
        activeSessionId={activeSession.id}
        onSelectSession={setActiveSessionId}
        onCreateSession={handleCreateSession}
      />

      <main className="main-content">
        <header className="topbar">
          <div>
            <h1>Chat com documentos via IA</h1>
            <p>
              FastAPI · Redis Vector Search · Sentence Transformers · LangGraph
            </p>
          </div>

          {health && (
            <div className={`status status-${health.status}`}>
              API: {health.api} · Redis: {health.redis}
            </div>
          )}
        </header>

        {error && <p className="error">{error}</p>}

        <div className="content-grid">
          <div className="left-column">
            <FileUpload onUploaded={handleUploaded} />
            <DocumentList documents={documents} onDeleted={handleDeleted} />
          </div>

          <ChatWindow
            activeSession={activeSession}
            onMessageSent={handleMessageSent}
          />
        </div>
      </main>
    </div>
  );
}