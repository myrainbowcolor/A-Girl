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


def test_mock_identity_reply():
    reply = MockLLMProvider().generate(_system(), [{"role": "user", "content": "你是人机吗"}])
    assert "AI" in reply or "小语" in reply
    assert "后来呢" not in reply
    assert "愿意多说" not in reply


def test_mock_closed_not_pushy():
    hist = [
        {"role": "user", "content": "..."},
        {"role": "assistant", "content": "嗯，我在呢。你先随便丢几个词给我也行~"},
        {"role": "user", "content": "..."},
    ]
    reply = MockLLMProvider().generate(_system(), hist)
    assert "后来呢" not in reply
    assert "愿意多说" not in reply
    assert reply != hist[1]["content"]


def test_mock_dont_know_how_to_start():
    reply = MockLLMProvider().generate(
        _system(), [{"role": "user", "content": "不知道怎么说开头"}]
    )
    assert "后来呢" not in reply
    assert any(w in reply for w in ("丢几个词", "不用", "陪着", "不急"))
