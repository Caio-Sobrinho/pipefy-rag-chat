const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

async function request(path, options = {}) {
  const response = await fetch(`${API_URL}${path}`, options);

  if (!response.ok) {
    let errorMessage = "Erro inesperado na requisição.";

    try {
      const data = await response.json();
      errorMessage = data.error || data.detail || errorMessage;
    } catch {
      errorMessage = await response.text();
    }

    throw new Error(
      typeof errorMessage === "string"
        ? errorMessage
        : JSON.stringify(errorMessage)
    );
  }

  return response.json();
}

export async function getHealth() {
  return request("/health");
}

export async function uploadDocument(file) {
  const formData = new FormData();
  formData.append("file", file);

  return request("/upload", {
    method: "POST",
    body: formData,
  });
}

export async function listDocuments() {
  return request("/documents");
}

export async function deleteDocument(fileId) {
  return request(`/documents/${fileId}`, {
    method: "DELETE",
  });
}

export async function sendChatMessage({ question, sessionId, topK = 3 }) {
  return request("/chat", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      question,
      session_id: sessionId,
      top_k: topK,
    }),
  });
}