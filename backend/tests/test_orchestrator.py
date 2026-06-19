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


def test_empathetic_reply_when_user_frustrated(orch):
    o, _, _ = orch
    res = o.chat("u1", "sess1", "我很烦")
    assert "我听到你说" not in res.reply
    assert res.avatar.animation == "comfort"
    assert res.avatar.expression == "担心"


def test_minor_adult_content_blocked_via_orchestrator(orch):
    o, _, _ = orch  # 默认 audience=minor
    res = o.chat("u1", "sess1", "你做我女朋友好不好")
    assert res.llm == "safety"
    assert res.safety_category == "adult"
    assert res.avatar.expression in {"微笑", "大笑", "平静", "惊讶", "难过", "担心"}


class _BadLLM:
    """模拟本地小模型乱回复，触发场景引擎补位。"""

    name = "openai_compatible:bad"

    def generate(self, system_prompt: str, messages: list[dict], temperature: float = 0.8) -> str:
        return "哈哈，很高兴你和我有相似之处，小确幸很多呢。"

    def generate_stream(self, system_prompt: str, messages: list[dict], temperature: float = 0.8):
        text = self.generate(system_prompt, messages, temperature=temperature)
        for i in range(0, len(text), 2):
            yield text[i : i + 2]


def test_scene_blend_on_bad_llm():
    with tempfile.NamedTemporaryFile(suffix=".db") as f:
        s = Settings(db_path=f.name, llm_mock_fallback=True)
        db = Database(f.name)
        mem = MemoryStore(db, HashEmbeddingProvider(dim=256), s)
        o = Orchestrator(db, mem, EmotionEngine(), _BadLLM(), s)
        try:
            res = o.chat("u1", "sess1", "我养了一只叫橘子的猫")
            assert "相似之处" not in res.reply
            assert "小确幸" not in res.reply
            assert "猫" in res.reply or "橘" in res.reply
        finally:
            db.close()

