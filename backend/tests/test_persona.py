from app.domain import EmotionState, Persona, Relationship
from app.persona import build_system_prompt


def test_prompt_forbids_fake_memory_when_empty():
    p = build_system_prompt(Persona(), EmotionState(), Relationship(), [])
    assert "禁止" in p and "你说过" in p
    assert "不是 ta 的" in p


def test_prompt_lists_only_factual_memories():
    from app.domain import Memory

    mems = [Memory(user_id="u1", content="ta 说：工作好多", created_at=0)]
    p = build_system_prompt(Persona(), EmotionState(), Relationship(), mems)
    assert "工作好多" in p
    assert "仅可引用" in p
