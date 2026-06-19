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


def test_prompt_user_turn_negative_when_npc_calm():
    """用户倾诉负面时，即使 NPC 内在仍平和，prompt 也应含共情侧重。"""
    calm = EmotionState(pleasure=0.5, arousal=0.3)
    p = build_system_prompt(
        Persona(), calm, Relationship(), [], user_text="回家还要哄娃，心好累"
    )
    assert "【本轮侧重】" in p
    assert "先接住感受" in p


def test_prompt_user_turn_positive():
    p = build_system_prompt(
        Persona(), EmotionState(), Relationship(), [], user_text="今天特别开心哈哈"
    )
    assert "【本轮侧重】" in p
    assert "替 ta 高兴" in p


def test_prompt_user_turn_neutral_omits_block():
    p = build_system_prompt(
        Persona(), EmotionState(), Relationship(), [], user_text="嗯"
    )
    assert "【本轮侧重】" not in p


def test_prompt_user_turn_nostalgic():
    p = build_system_prompt(
        Persona(), EmotionState(), Relationship(), [], user_text="好怀念小时候在老家"
    )
    assert "【本轮侧重】" in p
    assert "怀旧" in p
