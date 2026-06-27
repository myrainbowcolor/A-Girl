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
        Persona(), EmotionState(), Relationship(), [], user_text="今天要开会"
    )
    assert "【本轮侧重】" not in p


def test_prompt_user_turn_closed_minimal():
    p = build_system_prompt(
        Persona(), EmotionState(), Relationship(), [], user_text=".."
    )
    assert "【本轮侧重】" in p
    assert "尊重边界" in p


def test_prompt_user_turn_masked_low_haohao():
    p = build_system_prompt(
        Persona(), EmotionState(), Relationship(), [], user_text="还好"
    )
    assert "【本轮侧重】" in p
    assert "压着情绪" in p or "轻轻接住" in p
    assert "尊重边界" not in p.split("【本轮侧重】")[1].split("\n")[0]


def test_prompt_user_turn_masked_low_evasive():
    p = build_system_prompt(
        Persona(), EmotionState(), Relationship(), [], user_text="不知道"
    )
    assert "【本轮侧重】" in p
    assert "压着情绪" in p or "轻轻接住" in p
    assert "尊重边界" not in p.split("【本轮侧重】")[1].split("\n")[0]


def test_prompt_user_turn_masked_low_fatigue():
    p = build_system_prompt(
        Persona(), EmotionState(), Relationship(), [], user_text="累"
    )
    assert "【本轮侧重】" in p
    assert "压着情绪" in p or "轻轻接住" in p
    assert "尊重边界" not in p.split("【本轮侧重】")[1].split("\n")[0]


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


def test_prompt_user_turn_insomnia():
    """失眠反刍句应使用独立侧重，禁止助眠建议式指引。"""
    p = build_system_prompt(
        Persona(),
        EmotionState(),
        Relationship(),
        [],
        user_text="又失眠了，脑子停不下来",
    )
    assert "【本轮侧重】" in p
    assert "失眠" in p or "脑子停" in p
    assert "数羊" in p or "助眠" in p


def test_prompt_user_turn_sad_not_insomnia():
    """纯低落句不走失眠侧重。"""
    p = build_system_prompt(
        Persona(), EmotionState(), Relationship(), [], user_text="回家还要哄娃，心好累"
    )
    assert "【本轮侧重】" in p
    assert "数羊" not in p and "助眠" not in p


def test_prompt_user_turn_longing():
    """想念句应使用依恋侧重，禁止开心报喜指引。"""
    p = build_system_prompt(
        Persona(),
        EmotionState(),
        Relationship(affinity=80.0),
        [],
        user_text="好久没聊了，有点想你",
    )
    assert "【本轮侧重】" in p
    block = p.split("【本轮侧重】")[1].split("\n")[0]
    assert "想念" in block or "依恋" in block or "在乎" in block
    assert "禁止" in block and "报喜" in block


def test_prompt_user_turn_self_doubt():
    """自我怀疑句应使用独立侧重，而非通用低落共情。"""
    p = build_system_prompt(
        Persona(),
        EmotionState(),
        Relationship(),
        [],
        user_text="是不是我太差劲了",
    )
    assert "【本轮侧重】" in p
    block = p.split("【本轮侧重】")[1].split("\n")[0]
    assert "自我怀疑" in block or "跟别人比" in block
    assert "别比了" in block or "灌鸡汤" in block


def test_prompt_user_turn_comparison_self_doubt():
    p = build_system_prompt(
        Persona(),
        EmotionState(),
        Relationship(),
        [],
        user_text="同学都升职了，就我还原地踏步",
    )
    assert "【本轮侧重】" in p
    block = p.split("【本轮侧重】")[1].split("\n")[0]
    assert "自我怀疑" in block or "跟别人比" in block


def test_prompt_user_turn_sad_not_self_doubt():
    """纯低落句不走自我怀疑侧重。"""
    p = build_system_prompt(
        Persona(), EmotionState(), Relationship(), [], user_text="回家还要哄娃，心好累"
    )
    assert "【本轮侧重】" in p
    block = p.split("【本轮侧重】")[1].split("\n")[0]
    assert "先接住感受" in block
    assert "自我怀疑" not in block and "跟别人比" not in block
