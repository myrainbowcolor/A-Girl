import tempfile

from app.config import Settings
from app.db import Database
from app.domain import Relationship
from app.emotion import EmotionEngine
from app.llm import MockLLMProvider
from app.memory import HashEmbeddingProvider, MemoryStore
from app.orchestrator import Orchestrator


def test_unhappy_meta_complaint_not_city_reply():
    with tempfile.NamedTemporaryFile(suffix=".db") as f:
        db = Database(f.name)
        settings = Settings(reflection_every_n_memories=999, dialogue_strategy="scene_first")
        mem = MemoryStore(db, HashEmbeddingProvider(dim=256), settings)
        orch = Orchestrator(db, mem, EmotionEngine(), MockLLMProvider(), settings)
        uid, sid = "u", "s"
        rel = Relationship(affinity=45.0)
        rel.recompute_stage()
        db.save_relationship(uid, rel, 0.0)
        mem.add(uid, "ta 说：我想去杭州那座喜欢的城市", importance=5.0)

        msgs = [
            "最近总在回忆以前的事",
            "我不开心了",
            "我不开心了,为什么话要去回忆这些事情?你重要的不是应该首先安慰我吗?",
        ]
        replies = []
        for m in msgs:
            r = orch.chat(uid, sid, m).reply
            replies.append(r)

        assert "城市" not in replies[-1]
        assert "替你开心" not in replies[-1]
        assert "跟着开心" not in replies[1]
        assert any(w in replies[-1] for w in ("抱歉", "对不起", "对不起", "陪", "安慰", "接住"))
