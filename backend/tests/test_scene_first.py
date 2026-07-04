import tempfile

from app.config import Settings
from app.db import Database
from app.emotion import EmotionEngine
from app.llm import MockLLMProvider
from app.memory import HashEmbeddingProvider, MemoryStore
from app.orchestrator import Orchestrator


class _BadLLM:
    name = "openai_compatible:bad"

    def generate(self, system_prompt, messages, temperature=0.8):
        return "Hello! How can I assist you today?"

    def generate_stream(self, system_prompt, messages, temperature=0.8):
        t = self.generate(system_prompt, messages, temperature=temperature)
        yield t


def test_scene_first_avoids_generic_and_english():
    with tempfile.NamedTemporaryFile(suffix=".db") as f:
        s = Settings(
            db_path=f.name,
            dialogue_strategy="scene_first",
            scene_fallback=True,
        )
        db = Database(f.name)
        mem = MemoryStore(db, HashEmbeddingProvider(dim=256), s)
        o = Orchestrator(db, mem, EmotionEngine(), _BadLLM(), s)
        try:
            res = o.chat("u1", "s1", "随便聊聊")
            assert "assist" not in res.reply.lower()
            assert "愿意多说" not in res.reply
            res2 = o.chat("u1", "s1", "最近总觉得空空的")
            assert "后来呢" not in res2.reply
        finally:
            db.close()


def test_scene_first_compose_overtime_vent():
    """scene_first 下加班疲惫应由 compose 接住，而非问卷式 open 兜底。"""
    with tempfile.NamedTemporaryFile(suffix=".db") as f:
        s = Settings(db_path=f.name, dialogue_strategy="scene_first")
        db = Database(f.name)
        mem = MemoryStore(db, HashEmbeddingProvider(dim=256), s)
        o = Orchestrator(db, mem, EmotionEngine(), MockLLMProvider(), s)
        try:
            res = o.chat("u1", "s1", "今天加班到十点，好累")
            assert any(w in res.reply for w in ("加班", "辛苦", "累", "熬", "陪着"))
        finally:
            db.close()
