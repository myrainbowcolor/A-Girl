from app.memory_honesty import enforce_memory_honesty


def test_strip_fabricated_claim_when_no_memories():
    reply = "呀！我记得你说过你喜欢音乐和散步！"
    out = enforce_memory_honesty(reply, [], ["你好呀"])
    assert "你说过" not in out
    assert "音乐" not in out or "记错" in out or "我在听" in out


def test_keep_grounded_claim():
    reply = "你之前说过工作很多，今天还烦吗？"
    mem = type("M", (), {"content": "ta 说：工作好多"})()
    out = enforce_memory_honesty(reply, [mem], ["工作好多"])
    assert "工作" in out
