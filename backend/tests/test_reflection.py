import tempfile

from app.config import Settings
from app.db import Database
from app.domain import Persona
from app.llm import MockLLMProvider
from app.memory import HashEmbeddingProvider, MemoryStore
from app.memory.reflection import fallback_reflection, maybe_reflect


def test_fallback_reflection():
    text = fallback_reflection(["ta 说：今天开心", "ta 说：有点累"])
    assert "总结" in text


def test_maybe_reflect_triggers_on_interval():
    with tempfile.NamedTemporaryFile(suffix=".db") as f:
        s = Settings(db_path=f.name)
        db = Database(f.name)
        mem = MemoryStore(db, HashEmbeddingProvider(dim=256), s)
        user_id = "u-reflect"
        for i in range(3):
            mem.add(user_id, f"事件{i}", importance=3.0)
        insight = maybe_reflect(
            mem, user_id, every_n=3, llm=MockLLMProvider(),
            persona=Persona(), relationship_summary="",
        )
        assert insight is not None
        assert mem.count(user_id) >= 1  # reflection added
        db.close()
