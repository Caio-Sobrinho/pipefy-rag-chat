export function SessionSidebar({
  sessions,
  activeSessionId,
  onSelectSession,
  onCreateSession,
}) {
  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <h1>Pipefy RAG Chat</h1>

        <button onClick={onCreateSession}>Nova sessão</button>
      </div>

      <div className="session-list">
        {sessions.map((session) => (
          <button
            key={session.id}
            className={`session-item ${
              session.id === activeSessionId ? "active" : ""
            }`}
            onClick={() => onSelectSession(session.id)}
          >
            {session.name}
          </button>
        ))}
      </div>
    </aside>
  );
}