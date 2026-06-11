import json
import tempfile

import pytest
from fastapi.testclient import TestClient

from app.compliance import AgeGate
from app.config import Settings
from app.db import Database
from app.emotion import EmotionEngine
from app.llm import MockLLMProvider
from app.main import app
from app.memory import HashEmbeddingProvider, MemoryStore
from app.orchestrator import Orchestrator


@pytest.fixture
def client():
    with tempfile.NamedTemporaryFile(suffix=".db") as f:
        s = Settings(db_path=f.name)
        db = Database(f.name)
        mem = MemoryStore(db, HashEmbeddingProvider(dim=256), s)
        orch = Orchestrator(db, mem, EmotionEngine(), MockLLMProvider(), s)
        gate = AgeGate(db, require=True, min_age=0)

        import app.main as main_mod
        main_mod.settings = s
        main_mod._db = db
        main_mod._memory = mem
        main_mod._orchestrator = orch
        main_mod._age_gate = gate

        yield TestClient(app), db, gate
        db.close()


def _consent(client, user_id: str = "u-stream") -> None:
    client.post("/api/consent", json={"user_id": user_id, "age": 16})


def test_chat_stream_sse(client):
    c, _, _ = client
    _consent(c)
    with c.stream("POST", "/api/chat/stream", json={"user_id": "u-stream", "message": "你好"}) as resp:
        assert resp.status_code == 200
        chunks = []
        for line in resp.iter_lines():
            if line.startswith("data: "):
                chunks.append(json.loads(line[6:]))
        types = [x["type"] for x in chunks]
        assert "meta" in types
        assert "token" in types
        assert "done" in types
        done = next(x for x in chunks if x["type"] == "done")
        assert done["reply"]


def test_proactive_welcome(client):
    c, _, _ = client
    _consent(c, "u-new")
    r = c.get("/api/proactive/u-new")
    assert r.status_code == 200
    data = r.json()
    assert data["should_reach_out"] is True
    assert data["trigger"] == "welcome"
