"""用户输入语言检测与回复语言约束。"""
from __future__ import annotations

import re

_LANG_INSTRUCTION = {
    "zh": (
        "【语言】用户正在使用中文。你必须全程用中文回复：句子主体必须是中文，"
        "禁止整句或整段用英文作答（OK、AI 等常见缩写除外）。"
    ),
    "en": (
        "【Language】The user is writing in English. You must reply entirely in English. "
        "Do not switch to Chinese unless quoting the user's words."
    ),
    "mixed": (
        "【语言】用户使用中英混合。请用中文为主、口语化回复，可保留 user 用过的英文词，"
        "但不要突然改成全英文或全中文。"
    ),
}


def detect_user_language(text: str) -> str:
    """检测用户本轮主要语言：zh | en | mixed。"""
    if not text or not text.strip():
        return "zh"
    cjk = len(re.findall(r"[\u4e00-\u9fff]", text))
    latin = len(re.findall(r"[A-Za-z]", text))
    if cjk >= 2 and latin >= 2:
        return "mixed"
    if latin > cjk and latin >= 4:
        return "en"
    if cjk > 0:
        return "zh"
    if latin >= 4:
        return "en"
    return "zh"


def language_instruction(lang: str) -> str:
    return _LANG_INSTRUCTION.get(lang, _LANG_INSTRUCTION["zh"])


def reply_language_mismatch(user_lang: str, reply: str) -> bool:
    """回复语言是否与用户输入明显不一致。"""
    if not reply or not reply.strip():
        return False
    cjk = len(re.findall(r"[\u4e00-\u9fff]", reply))
    latin = len(re.findall(r"[A-Za-z]", reply))
    if user_lang in ("zh", "mixed"):
        return cjk <= 2 and latin >= 10
    if user_lang == "en":
        return cjk >= 6 and cjk > latin
    return False
