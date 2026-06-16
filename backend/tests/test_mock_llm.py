import pytest

from app.llm.mock import MockLLMProvider


def _system(stage: str = "陌生") -> str:
    return f"你的名字：小语\n当前情绪：有些焦虑/委屈\n关系阶段：{stage}（亲密度 5/100）"


@pytest.mark.parametrize("msg", ["我很烦", "好烦啊", "今天好生气"])
def test_mock_empathy_for_frustration(msg):
    reply = MockLLMProvider().generate(_system(), [{"role": "user", "content": msg}])
    assert "我听到你说" not in reply
    assert "愉悦度" not in reply
    assert any(w in reply for w in ("烦", "堵", "陪", "在呢", "呼吸"))


def test_mock_empathy_for_sadness():
    reply = MockLLMProvider().generate(_system("朋友"), [{"role": "user", "content": "我很难过"}])
    assert "难过" in reply or "陪" in reply


def test_mock_warm_for_positive():
    reply = MockLLMProvider().generate(_system(), [{"role": "user", "content": "今天好开心"}])
    assert "开心" in reply


def test_mock_insomnia_multiturn_not_repetitive():
    """失眠多轮应换说法，避免与首轮完全重复。"""
    sys_prompt = _system("熟悉")
    msgs = [{"role": "user", "content": "又失眠了，脑子停不下来"}]
    first = MockLLMProvider().generate(sys_prompt, msgs)
    msgs.append({"role": "assistant", "content": first})
    msgs.append({"role": "user", "content": "越躺越清醒，好烦"})
    third = MockLLMProvider().generate(sys_prompt, msgs)
    assert third != first
    assert any(w in third for w in ("陪", "懂", "烦", "磨人"))
