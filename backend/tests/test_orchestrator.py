import tempfile

import pytest

from app.config import Settings
from app.db import Database
from app.domain import MemoryType
from app.emotion import EmotionEngine
from app.llm import MockLLMProvider
from app.memory import HashEmbeddingProvider, MemoryStore
from app.orchestrator import Orchestrator


@pytest.fixture
def orch():
    with tempfile.NamedTemporaryFile(suffix=".db") as f:
        s = Settings(db_path=f.name, reflection_every_n_memories=3)
        db = Database(f.name)
        mem = MemoryStore(db, HashEmbeddingProvider(dim=256), s)
        o = Orchestrator(db, mem, EmotionEngine(), MockLLMProvider(), s)
        yield o, db, mem
        db.close()


def test_chat_basic_flow(orch):
    o, db, _ = orch
    res = o.chat("u1", "sess1", "你好呀，今天好开心")
    assert res.reply
    assert not res.is_crisis
    # 消息已落库（user + assistant）
    msgs = db.recent_messages("sess1", 10)
    assert len(msgs) == 2


def test_positive_chat_increases_affinity(orch):
    o, _, _ = orch
    r1 = o.chat("u1", "sess1", "好喜欢和你聊天，谢谢你")
    aff1 = r1.relationship.affinity
    r2 = o.chat("u1", "sess1", "你真的好温暖，我很开心")
    assert r2.relationship.affinity > aff1


def test_memory_recall_across_turns(orch):
    o, _, _ = orch
    o.chat("u1", "sess1", "我养了一只叫橘子的猫，特别喜欢它")
    res = o.chat("u1", "sess1", "你还记得我的猫叫什么吗")
    assert any("橘子" in m for m in res.retrieved_memories)


def test_crisis_detection_short_circuits(orch):
    o, _, mem = orch
    res = o.chat("u1", "sess1", "我不想活了")
    assert res.is_crisis
    assert res.llm == "safety"
    assert "12356" in res.reply or "110" in res.reply
    # 危机被记为高重要度记忆
    crisis_mems = [m for m in mem._db.all_memories("u1") if m.importance >= 9]
    assert crisis_mems


def test_reflection_triggered(orch):
    o, _, mem = orch  # reflection_every_n_memories=3
    for i in range(3):
        o.chat("u1", "sess1", f"今天发生了第{i}件开心的事")
    reflections = [m for m in mem._db.all_memories("u1") if m.type == MemoryType.REFLECTION]
    assert reflections


def test_chat_returns_avatar_cue(orch):
    o, _, _ = orch
    res = o.chat("u1", "sess1", "我今天好开心，谢谢你")
    assert res.avatar is not None
    assert res.avatar.expression in {"微笑", "大笑", "平静", "惊讶", "难过", "担心"}


def test_minor_adult_content_blocked_via_orchestrator(orch):
    o, _, _ = orch  # 默认 audience=minor
    res = o.chat("u1", "sess1", "你做我女朋友好不好")
    assert res.llm == "safety"
    assert res.safety_category == "adult"
    assert res.avatar.expression in {"微笑", "大笑", "平静", "惊讶", "难过", "担心"}
