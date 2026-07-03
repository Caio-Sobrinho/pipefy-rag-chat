import { useState } from "react";
import { uploadDocument } from "../api/client";

export function FileUpload({ onUploaded }) {
  const [file, setFile] = useState(null);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState("");

  async function handleUpload(event) {
    event.preventDefault();

    if (!file) {
      setError("Selecione um arquivo PDF, TXT ou DOCX.");
      return;
    }

    try {
      setError("");
      setIsUploading(true);

      const result = await uploadDocument(file);

      setFile(null);
      onUploaded(result);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsUploading(false);
    }
  }

  return (
    <section className="card">
      <h2>Upload de documentos</h2>

      <form onSubmit={handleUpload} className="upload-form">
        <input
          type="file"
          accept=".pdf,.txt,.docx"
          onChange={(event) => setFile(event.target.files?.[0] || null)}
        />

        <button type="submit" disabled={isUploading}>
          {isUploading ? "Indexando..." : "Enviar documento"}
        </button>
      </form>

      {file && <p className="muted">Arquivo selecionado: {file.name}</p>}

      {error && <p className="error">{error}</p>}
    </section>
  );
}