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


def test_mock_longing_miss_you_not_cheer():
    """亲密想念应柔软回应，不走开心报喜分支。"""
    reply = MockLLMProvider().generate(
        _system("亲密"),
        [{"role": "user", "content": "好久没聊了，有点想你"}],
    )
    assert "想你" in reply or "好久" in reply
    assert "跟着开心起来了" not in reply
    assert "报喜" not in reply


def test_mock_stranger_continue_chat_natural():
    """陌生关系续聊应口语化，禁止嗯嗯开头与欢迎随时客服腔。"""
    reply = MockLLMProvider().generate(
        _system("陌生"),
        [{"role": "user", "content": "明天还想来找你聊聊"}],
    )
    assert not reply.lstrip().startswith("嗯")
    assert "欢迎随时" not in reply
    assert any(w in reply for w in ("开心", "高兴", "真好", "棒"))


def test_mock_intimate_lean_on_fatigue():
    """亲密「想靠着你说说」应接住倚靠意愿，不走泛化负面套话。"""
    reply = MockLLMProvider().generate(
        _system("亲密"),
        [{"role": "user", "content": "今天过得好累，想靠着你说说"}],
    )
    assert any(w in reply for w in ("靠", "陪", "抱抱"))
    assert "不太好受" not in reply


def test_mock_homesickness_short():
    """短句「想家了」应接住思念空落，非问卷式兜底。"""
    reply = MockLLMProvider().generate(
        _system("朋友"),
        [{"role": "user", "content": "想家了"}],
    )
    assert any(w in reply for w in ("想家", "家", "空", "陪", "难受", "思念"))
    assert "慢慢讲" not in reply
    assert "好，我收到了" not in reply
    assert not reply.lstrip().startswith("嗯")


def test_mock_disappointment_short():
    """短句「好失望」应接住失落感，非空串/问卷兜底。"""
    reply = MockLLMProvider().generate(
        _system("熟悉"),
        [{"role": "user", "content": "好失望"}],
    )
    assert reply
    assert any(w in reply for w in ("不太好受", "陪", "听", "难受", "心疼"))
    assert "好，我收到了" not in reply
    assert not reply.lstrip().startswith("嗯")


def test_mock_rumination_short():
    """短句「内耗」应接住内耗感，非空串/问卷兜底。"""
    reply = MockLLMProvider().generate(
        _system("熟悉"),
        [{"role": "user", "content": "内耗"}],
    )
    assert reply
    assert any(w in reply for w in ("不太好受", "陪", "听", "难受", "心疼"))
    assert "好，我收到了" not in reply
    assert not reply.lstrip().startswith("嗯")


def test_mock_shame_short():
    """短句「好丢脸」应接住丢脸感，非空串/问卷兜底。"""
    reply = MockLLMProvider().generate(
        _system("熟悉"),
        [{"role": "user", "content": "好丢脸"}],
    )
    assert reply
    assert any(w in reply for w in ("丢脸", "丢人", "找地缝", "陪", "听"))
    assert "好，我收到了" not in reply
    assert not reply.lstrip().startswith("嗯")


def test_mock_inferiority_short():
    """短句「好自卑」应接住自卑感，非空串/问卷兜底，且非升职比较话术。"""
    reply = MockLLMProvider().generate(
        _system("熟悉"),
        [{"role": "user", "content": "好自卑"}],
    )
    assert reply
    assert any(w in reply for w in ("自卑", "不够好", "否定", "陪"))
    assert "升职" not in reply
    assert "原地踏步" not in reply
    assert "好，我收到了" not in reply
    assert not reply.lstrip().startswith("嗯")


def test_mock_useless_feeling_short():
    """短句「好没用」应接住自我否定，勿套用冲动消费后悔话术。"""
    reply = MockLLMProvider().generate(
        _system("熟悉"),
        [{"role": "user", "content": "好没用"}],
    )
    assert reply
    assert any(w in reply for w in ("没用", "自我否定", "陪"))
    assert "管不住手" not in reply
    assert "后悔" not in reply
    assert "乱花钱" not in reply
    assert "好，我收到了" not in reply
    assert not reply.lstrip().startswith("嗯")


@pytest.mark.parametrize(
    "utterance",
    ["被裁了", "裁员了", "被开除了", "失业了", "丢工作了"],
)
def test_mock_layoff_short(utterance: str):
    """短句失业/裁员应接住失落，非空串/问卷兜底，且非工作压力话术。"""
    reply = MockLLMProvider().generate(
        _system("熟悉"),
        [{"role": "user", "content": utterance}],
    )
    assert reply
    assert any(
        w in reply
        for w in ("被裁", "裁", "开除", "失业", "丢工作", "丢了工作", "陪", "听")
    )
    assert "忙不过来" not in reply
    assert "不公平" not in reply
    assert "好，我收到了" not in reply
    assert not reply.lstrip().startswith("嗯")


@pytest.mark.parametrize(
    "utterance",
    ["被鸽了", "放鸽子了", "放我鸽子", "又被鸽了", "他放我鸽子了", "爽约了"],
)
def test_mock_stood_up_short(utterance: str):
    """短句被鸽/放鸽子应接住失落委屈，非空串/问卷兜底，且非失恋分手话术。"""
    reply = MockLLMProvider().generate(
        _system("熟悉"),
        [{"role": "user", "content": utterance}],
    )
    assert reply
    assert any(
        w in reply
        for w in ("被鸽", "放鸽子", "鸽子", "爽约", "陪", "听", "空", "委屈", "伤")
    )
    assert "分手" not in reply
    assert "失恋" not in reply
    assert "好，我收到了" not in reply
    assert not reply.lstrip().startswith("嗯")
