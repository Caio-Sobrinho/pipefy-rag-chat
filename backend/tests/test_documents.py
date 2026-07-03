def test_list_documents_after_upload(client, sample_txt_file):
    upload_response = client.post("/upload", files=sample_txt_file)

    assert upload_response.status_code == 200

    response = client.get("/documents")

    assert response.status_code == 200

    documents = response.json()

    assert len(documents) >= 1
    assert documents[0]["name"] == "sample.txt"
    assert documents[0]["chunks"] >= 1


def test_list_document_chunks_after_upload(client, sample_txt_file):
    upload_response = client.post("/upload", files=sample_txt_file)
    file_id = upload_response.json()["file_id"]

    response = client.get(f"/documents/{file_id}/chunks")

    assert response.status_code == 200

    chunks = response.json()

    assert len(chunks) >= 1
    assert chunks[0]["file_id"] == file_id
    assert chunks[0]["source"] == "sample.txt"
    assert chunks[0]["has_embedding"] is True
    assert chunks[0]["embedding_dimension"] == 384
    assert chunks[0]["embedding"] is None


def test_delete_document_after_upload(client, sample_txt_file):
    upload_response = client.post("/upload", files=sample_txt_file)
    file_id = upload_response.json()["file_id"]

    delete_response = client.delete(f"/documents/{file_id}")

    assert delete_response.status_code == 200

    data = delete_response.json()

    assert data["deleted"] is True
    assert data["file_id"] == file_id


def test_delete_unknown_document_returns_404(client):
    response = client.delete("/documents/non-existent-id")

    assert response.status_code == 404

    data = response.json()

    assert data["error"] == "Document not found."