import { deleteDocument } from "../api/client";

export function DocumentList({ documents, onDeleted }) {
  async function handleDelete(fileId) {
    const confirmed = window.confirm("Deseja remover este documento?");

    if (!confirmed) return;

    await deleteDocument(fileId);
    onDeleted(fileId);
  }

  return (
    <section className="card">
      <h2>Documentos indexados</h2>

      {documents.length === 0 ? (
        <p className="muted">Nenhum documento enviado ainda.</p>
      ) : (
        <div className="document-list">
          {documents.map((document) => (
            <div key={document.file_id} className="document-item">
              <div>
                <strong>{document.name}</strong>
                <p className="muted">
                  {document.chunks} chunks · status: {document.status}
                </p>
              </div>

              <button
                className="danger"
                onClick={() => handleDelete(document.file_id)}
              >
                Remover
              </button>
            </div>
          ))}
        </div>
      )}
    </section>
  );
}