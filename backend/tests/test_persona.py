from app.domain import EmotionState, Persona, Relationship
from app.persona import build_system_prompt


def test_prompt_includes_virtual_world_boundary():
    p = build_system_prompt(Persona(), EmotionState(), Relationship(), [])
    assert "【虚拟世界边界】" in p
    assert "现实国家" in p
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
        Persona(), EmotionState(), Relationship(), [], user_text="今天天气不错"
    )
    assert "【本轮侧重】" not in p


def test_prompt_user_turn_closed_minimal():
    p = build_system_prompt(
        Persona(), EmotionState(), Relationship(), [], user_text=".."
    )
    assert "【本轮侧重】" in p
    assert "尊重边界" in p


def test_prompt_user_turn_meta_pushback():
    p = build_system_prompt(
        Persona(), EmotionState(), Relationship(), [], user_text="为啥一定要跟你聊天?"
    )
    assert "【本轮侧重】" in p
    assert "不强迫" in p


def test_prompt_user_turn_identity():
    p = build_system_prompt(
        Persona(), EmotionState(), Relationship(), [], user_text="你是机器人吗"
    )
    assert "【本轮侧重】" in p
    assert "AI" in p


def test_prompt_user_turn_nostalgic():
    p = build_system_prompt(
        Persona(), EmotionState(), Relationship(), [], user_text="好怀念小时候在老家"
    )
    assert "【本轮侧重】" in p
    assert "怀旧" in p


def test_prompt_user_turn_angry():
    """愤怒发泄句应使用独立侧重，而非通用低落共情。"""
    p = build_system_prompt(
        Persona(),
        EmotionState(),
        Relationship(),
        [],
        user_text="老板今天当众骂我，气死了！",
    )
    assert "【本轮侧重】" in p
    assert "火气" in p or "怒气" in p
    assert "先接住这股火" in p


def test_prompt_user_turn_sad_not_angry():
    """纯低落句仍走通用负向共情侧重。"""
    p = build_system_prompt(
        Persona(), EmotionState(), Relationship(), [], user_text="回家还要哄娃，心好累"
    )
    assert "【本轮侧重】" in p
    assert "先接住感受" in p
    assert "火气" not in p and "怒气" not in p
