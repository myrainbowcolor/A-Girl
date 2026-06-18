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


def test_mock_memory_recall_pet_name():
    system = (
        "你的名字：小语\n当前情绪：平和\n关系阶段：朋友（亲密度 48/100）\n\n"
        "【关于 ta 的已知事实（仅可引用以下内容，不得超出）】\n"
        "- ta 说：我养了一只叫橘子的猫，超粘人\n\n"
        "【回复要求】\n"
    )
    reply = MockLLMProvider().generate(
        system,
        [
            {"role": "user", "content": "我养了一只叫橘子的猫，超粘人"},
            {"role": "assistant", "content": "养猫呀！"},
            {"role": "user", "content": "你还记得我的猫叫什么吗"},
        ],
    )
    assert "橘子" in reply
    assert "记得" in reply
    assert "ta 说：" not in reply


def test_mock_pet_antics_followup():
    """宠物续聊应接住捣蛋细节，而非泛化开心报喜句。"""
    system = (
        "你的名字：小语\n当前情绪：开心\n关系阶段：朋友（亲密度 48/100）\n\n"
        "【关于 ta 的已知事实（仅可引用以下内容，不得超出）】\n"
        "- ta 说：我养了一只叫橘子的猫，超粘人\n\n"
        "【回复要求】\n"
    )
    reply = MockLLMProvider().generate(
        system,
        [
            {"role": "user", "content": "我养了一只叫橘子的猫，超粘人"},
            {"role": "assistant", "content": "养猫呀！粘人的小家伙最会撒娇了～"},
            {"role": "user", "content": "它今天又把杯子打翻了哈哈"},
        ],
    )
    assert "橘子" in reply
    assert any(w in reply for w in ("打翻", "杯子", "捣蛋"))
    assert "跟着开心起来了" not in reply


def test_mock_breakup_crying_empathy():
    reply = MockLLMProvider().generate(
        _system("朋友"),
        [
            {"role": "user", "content": "我们分手了"},
            {"role": "assistant", "content": "分手真的很难扛。"},
            {"role": "user", "content": "我还是忍不住想哭"},
        ],
    )
    assert any(w in reply for w in ("哭", "陪", "分手"))
    assert "不太好受" not in reply
