from pathlib import Path
import sys

from fastapi.testclient import TestClient

sys.path.append(str(Path(__file__).resolve().parents[1]))

from main import app


client = TestClient(app)


def test_root_healthcheck() -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {"message": "This is an LLM integrated Notes APP"}
