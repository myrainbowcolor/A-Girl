from app.domain import Memory, MemoryType
from app.knowledge_scope import KNOWLEDGE_SCOPE_ID
from app.persona import build_system_prompt, default_persona
from app.domain import EmotionState, Relationship


def test_prompt_includes_knowledge_section():
    user_mem = Memory(
        user_id="u1",
        content="ta 说：今天心好累",
        type=MemoryType.EPISODIC,
        importance=5,
        embedding=[0.1],
        created_at=0,
        last_access=0,
    )
    know_mem = Memory(
        user_id=KNOWLEDGE_SCOPE_ID,
        content="[知识:goutoujunshi/01-test.md#测试]\n先接住情绪，再谈策略。",
        type=MemoryType.SEMANTIC,
        importance=8,
        embedding=[0.2],
        created_at=0,
        last_access=0,
    )
    prompt = build_system_prompt(
        default_persona(), EmotionState(), Relationship(), [user_mem, know_mem]
    )
    assert "可参考知识" in prompt
    assert "先接住情绪" in prompt
    assert "心好累" in prompt
