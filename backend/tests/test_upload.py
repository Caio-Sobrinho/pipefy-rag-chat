def test_upload_txt_document_returns_indexed_local_status(client, sample_txt_file):
    response = client.post("/upload", files=sample_txt_file)

    assert response.status_code == 200

    data = response.json()

    assert data["file_id"]
    assert data["name"] == "sample.txt"
    assert data["chunks_indexed"] >= 1
    assert data["embeddings_generated"] == data["chunks_indexed"]
    assert data["embedding_dimension"] == 384
    assert data["redis_indexed"] is False
    assert data["status"] == "indexed_local"


def test_upload_rejects_unsupported_file_type(client):
    files = {
        "file": (
            "malware.exe",
            b"fake content",
            "application/octet-stream",
        )
    }

    response = client.post("/upload", files=files)

    assert response.status_code == 400

    data = response.json()

    assert "Unsupported file type" in data["error"]