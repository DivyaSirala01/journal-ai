from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_root_healthcheck() -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {"message": "This is an LLM integrated Notes APP"}
