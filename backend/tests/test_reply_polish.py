"""回复润色单元测试。"""
from app.reply_polish import polish_reply


def test_collapse_triple_question_marks():
    out = polish_reply("你今天怎么样？？？发生什么了？")
    assert "???" not in out
    assert "？？？" not in out


def test_limit_one_question_per_reply():
    out = polish_reply("你还好吗？后来怎么样了？是不是很难过？")
    assert out.count("？") + out.count("?") <= 1


def test_remove_robotic_tone():
    out = polish_reply("很高兴为您服务！你今天怎么样？")
    assert "很高兴为您服务" not in out


def test_preserves_natural_single_question():
    out = polish_reply("听起来你今天挺累的，要不要先歇一会儿？")
    assert "？" in out or "?" in out


def test_preserves_empathy_without_question_spam():
    src = "嗯……听起来你心里挺堵的。我在呢，不用急着说清楚。"
    assert polish_reply(src) == src
