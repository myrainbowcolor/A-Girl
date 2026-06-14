"""回复润色：去机械腔、压缩多余问号、限制问卷式连问。"""
from __future__ import annotations

import re

# 模型偶发输出的机械/客服腔
_ROBOTIC_PHRASES = (
    "作为一个AI", "作为人工智能", "很高兴为您服务", "有什么可以帮您",
    "请问还有什么", "我听到了你说", "根据你的描述",
)

# 连续问号 / 中英文问号混用
_MULTI_Q = re.compile(r"[\?？]{2,}")

# Markdown / 列表痕迹
_LIST_LINE = re.compile(r"^\s*(?:[-*•]|\d+[.)])\s+", re.MULTILINE)

# 句末拆分（保留分隔符）
_SENT_SPLIT = re.compile(r"(?<=[。！？!?])")


def _is_question_sentence(sent: str) -> bool:
    s = sent.strip()
    if not s:
        return False
    if s.endswith(("?", "？")):
        return True
    return any(
        p in s
        for p in ("吗", "呢", "么", "是不是", "有没有", "能不能", "可不可以", "对吧")
    ) and len(s) <= 48


def _to_statement(sent: str) -> str:
    """把多余问句弱化成陈述，避免问卷感。"""
    s = sent.strip()
    s = s.rstrip("?？")
    for tail in ("吗", "呢", "么"):
        if s.endswith(tail) and len(s) > 2:
            s = s[: -len(tail)]
            break
    if s and s[-1] not in "。！…":
        s += "。"
    return s


def _limit_questions(text: str, max_questions: int = 1) -> str:
    parts = _SENT_SPLIT.split(text)
    out: list[str] = []
    q_count = 0
    for part in parts:
        if not part.strip():
            continue
        if _is_question_sentence(part):
            q_count += 1
            if q_count > max_questions:
                out.append(_to_statement(part))
                continue
        out.append(part)
    return "".join(out).strip()


def polish_reply(text: str) -> str:
    """让 LLM 回复更接近真人微信聊天。"""
    if not text or not text.strip():
        return text

    reply = text.strip()
    reply = _LIST_LINE.sub("", reply)
    for phrase in _ROBOTIC_PHRASES:
        reply = reply.replace(phrase, "")
    reply = re.sub(r"\n{2,}", "\n", reply).strip()
    reply = _MULTI_Q.sub("？", reply)
    reply = re.sub(r"\?\s*？", "？", reply)
    reply = re.sub(r"？\s*\?", "？", reply)

    # 去掉括号动作描写堆砌（保留偶尔一条）
    action_lines = re.findall(r"（[^）]{2,20}）", reply)
    if len(action_lines) >= 2:
        for extra in action_lines[1:]:
            reply = reply.replace(extra, "", 1)

    reply = _limit_questions(reply, max_questions=1)

    # 再次压缩尾部多余问号
    reply = re.sub(r"([。！…])？+", r"\1", reply)
    reply = re.sub(r"？+$", "？", reply)
    reply = _MULTI_Q.sub("？", reply)

    reply = re.sub(r"\s+", " ", reply).strip()
    return reply if reply else text.strip()
