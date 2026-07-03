export function SourceList({ sources }) {
  if (!sources || sources.length === 0) {
    return null;
  }

  return (
    <details className="sources">
      <summary>Fontes usadas ({sources.length})</summary>

      <div className="source-list">
        {sources.map((source, index) => (
          <div key={`${source.source}-${index}`} className="source-item">
            <strong>
              {index + 1}. {source.source}
            </strong>

            <p className="muted">Score: {source.score.toFixed(4)}</p>

            <p>{source.chunk}</p>
          </div>
        ))}
      </div>
    </details>
  );
}