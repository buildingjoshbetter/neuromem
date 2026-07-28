"""HTTP API for feeding external text sources into TrueMemory."""

from dataclasses import asdict
from typing import Any

from fastapi import FastAPI
from pydantic import BaseModel, Field

from truememory.ingest import ingest_text


class IngestRequest(BaseModel):
    text: str = Field(min_length=1)
    source_type: str = Field(min_length=1, max_length=50, pattern=r"^[a-zA-Z][\w-]*$")
    metadata: dict[str, Any] = Field(default_factory=dict)


app = FastAPI(title="TrueMemory Ingest API")


@app.post("/api/ingest")
def ingest(request: IngestRequest) -> dict[str, Any]:
    """Extract and persist durable facts from a conversation, document, or note."""
    provenance = {**request.metadata, "source_type": request.source_type.lower()}
    result = ingest_text(
        request.text,
        user_id=str(request.metadata.get("user_id", "")),
        session_id=str(request.metadata.get("session_id", "")),
        metadata=provenance,
        source_type=request.source_type,
    )
    return asdict(result)
