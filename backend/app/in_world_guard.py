"""游戏内回复边界：拦截客服腔、英文跑偏、教程体。"""
from __future__ import annotations

import re

from .language import detect_user_language
from .out_of_world_guard import (
    reply_looks_factual_encyclopedia,
    reply_uses_real_world_cognition,
    user_asks_out_of_world,
)

_OUT_OF_WORLD_MARKERS = (
    "How can I assist",
    "language model",
    "OpenAI",
    "作为一个AI",
    "作为一个 AI",
    "人工智能助手",
    "我可以帮你写",
    "以下是",
    "首先，",
    "其次，",
    "作为语言模型",
)
_ENGLISH_HEAVY_RE = re.compile(r"[A-Za-z]{4,}")


def reply_in_world_ok(reply: str, user_text: str) -> bool:
    """回复是否留在游戏/陪伴语境内。"""
    if not reply or not reply.strip():
        return False
    if reply_uses_real_world_cognition(reply, user_text):
        return False
    if user_asks_out_of_world(user_text) and reply_looks_factual_encyclopedia(reply):
        return False
    if reply_looks_factual_encyclopedia(reply):
        return False
    if any(m in reply for m in _OUT_OF_WORLD_MARKERS):
        return False
    lang = detect_user_language(user_text)
    if lang == "zh":
        letters = len(_ENGLISH_HEAVY_RE.findall(reply))
        if letters >= 3 or (reply.strip().startswith("Hello") and "小语" not in reply):
            return False
        if len(reply) > 20 and sum(c.isascii() and c.isalpha() for c in reply) > len(reply) * 0.45:
            return False
    return True
