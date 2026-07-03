def test_chat_without_documents_returns_no_context_message(client):
    payload = {
        "question": "O que o documento fala sobre IA?",
        "session_id": "test-session-empty",
        "top_k": 3,
    }

    response = client.post("/chat", json=payload)

    assert response.status_code == 200

    data = response.json()

    assert data["session_id"] == "test-session-empty"
    assert data["sources"] == []
    assert "Não encontrei trechos relevantes" in data["answer"]


def test_chat_with_uploaded_document_returns_answer_and_sources(client, sample_txt_file):
    upload_response = client.post("/upload", files=sample_txt_file)

    assert upload_response.status_code == 200

    payload = {
        "question": "O que o time de Data e AI faz?",
        "session_id": "test-session-rag",
        "top_k": 3,
    }

    response = client.post("/chat", json=payload)

    assert response.status_code == 200

    data = response.json()

    assert data["session_id"] == "test-session-rag"
    assert data["answer"] == "Resposta gerada pelo mock do LLM com base no contexto recuperado."
    assert len(data["sources"]) >= 1
    assert data["sources"][0]["source"] == "sample.txt"
    assert "Data e AI" in data["sources"][0]["chunk"]