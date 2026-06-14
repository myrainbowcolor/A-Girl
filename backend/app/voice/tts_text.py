"""TTS 朗读前文本清洗：去掉颜文字、emoji 等不应读出的符号。"""
from __future__ import annotations

import re

# Unicode emoji（勿使用跨 BMP 的大范围，避免误删中文）
_EMOJI = re.compile(
    "["
    "\U0001F600-\U0001F64F"
    "\U0001F300-\U0001F5FF"
    "\U0001F680-\U0001F6FF"
    "\U0001F1E0-\U0001F1FF"
    "\U0001F900-\U0001F9FF"
    "\U00002600-\U000026FF"
    "\U00002702-\U000027B0"
    "\u200d\ufe0f"
    "]+",
    flags=re.UNICODE,
)

# 括号颜文字：(´・ω・`) （T_T） 等
_KAOMOJI_PARENS = re.compile(
    r"[\(（]"
    r"[^)）\n]{0,48}"
    r"[´`^~\-_=oO0ωWaApPДツノヽゝゞ・.｡･∀；へ：]"
    r"[^)）\n]{0,48}"
    r"[\)）]"
)

# 独立 ASCII 颜文字 / 表情
_ASCII_EMOTICON = re.compile(
    r"(?<!\w)"
    r"(?:"
    r"\^[_\-]?[\^oO]|"
    r"\(T[_\-]?T\)|"
    r">_<|"
    r"\(\/?\_\/\)|"
    r"orz|"
    r"[:;=8]-?[DPp3oO\)\]\\|/]|"
    r"xD+|XD+"
    r")"
    r"(?!\w)",
    re.IGNORECASE,
)


def strip_for_tts(text: str) -> str:
    """移除 emoji、颜文字等，保留可读语言内容。"""
    if not text:
        return text
    cleaned = _EMOJI.sub("", text)
    cleaned = _KAOMOJI_PARENS.sub("", cleaned)
    cleaned = _ASCII_EMOTICON.sub("", cleaned)
    cleaned = re.sub(r"[ \t]+", " ", cleaned)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    cleaned = cleaned.strip()
    if cleaned:
        return cleaned
    fallback = _EMOJI.sub("", text).strip()
    return fallback or text.strip()
