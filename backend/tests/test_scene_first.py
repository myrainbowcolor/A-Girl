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
            llm_mock_fallback=True,
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


def test_scene_first_uses_mock_for_overtime():
    with tempfile.NamedTemporaryFile(suffix=".db") as f:
        s = Settings(db_path=f.name, dialogue_strategy="scene_first")
        db = Database(f.name)
        mem = MemoryStore(db, HashEmbeddingProvider(dim=256), s)
        o = Orchestrator(db, mem, EmotionEngine(), MockLLMProvider(), s)
        try:
            res = o.chat("u1", "s1", "今天加班到十点，好累")
            assert "加班" in res.reply or "辛苦" in res.reply
        finally:
            db.close()
