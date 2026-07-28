from dataclasses import dataclass

from fastapi.testclient import TestClient

import truememory.ingest.api as api


@dataclass
class _Result:
    facts_stored: int = 1


def test_document_ingest_routes_with_source_context_and_metadata(monkeypatch):
    calls = []
    monkeypatch.setattr(api, "ingest_text", lambda text, **kwargs: calls.append((text, kwargs)) or _Result())

    response = TestClient(api.app).post(
        "/api/ingest",
        json={
            "text": "A durable architecture decision that should be remembered.",
            "source_type": "document",
            "metadata": {"title": "ADR 1", "user_id": "alice"},
        },
    )

    assert response.status_code == 200
    assert response.json() == {"facts_stored": 1}
    assert calls[0][0] == "A durable architecture decision that should be remembered."
    assert calls[0][1]["user_id"] == "alice"
    assert calls[0][1]["metadata"]["source_type"] == "document"
    assert calls[0][1]["source_type"] == "document"


def test_conversation_is_not_wrapped(monkeypatch):
    calls = []
    monkeypatch.setattr(api, "ingest_text", lambda text, **kwargs: calls.append(text) or _Result())

    response = TestClient(api.app).post(
        "/api/ingest",
        json={"text": "User: I prefer dark mode for every application.", "source_type": "conversation"},
    )

    assert response.status_code == 200
    assert calls == ["User: I prefer dark mode for every application."]
