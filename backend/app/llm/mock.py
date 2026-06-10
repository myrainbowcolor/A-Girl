"""离线 Mock Provider。

不依赖外部 API，根据 system 提示中的情绪/关系线索与用户最后一句话，
生成有"人味"且能体现内部状态的确定性回复，便于无 Key 环境下验证整条编排链路。
"""
from __future__ import annotations

import re

from .base import LLMProvider


def _extract(tag: str, text: str, default: str = "") -> str:
    m = re.search(rf"{tag}：(.+)", text)
    return m.group(1).strip() if m else default


def _has_any(text: str, words: tuple[str, ...]) -> bool:
    return any(w in text for w in words)


def _pick(seed: str, options: list[str]) -> str:
    return options[hash(seed) % len(options)]


class MockLLMProvider(LLMProvider):
    @property
    def name(self) -> str:
        return "mock"

    def generate(self, system_prompt: str, messages: list[dict], temperature: float = 0.8) -> str:
        user_last = ""
        for m in reversed(messages):
            if m["role"] == "user":
                user_last = m["content"]
                break

        emotion = _extract("当前情绪", system_prompt, "平和")
        stage = _extract("关系阶段", system_prompt, "陌生")
        name = _extract("你的名字", system_prompt, "小语")

        endearment = {
            "陌生": "",
            "熟悉": "",
            "朋友": "嘿，",
            "亲密": "嗯，",
        }.get(stage, "")

        intimate_suffix = "呀" if stage in ("朋友", "亲密") else ""

        if _has_any(emotion, ("低落", "委屈", "焦虑")):
            mood_hint = "（语气放轻）"
        elif _has_any(emotion, ("开心", "兴奋", "满足")):
            mood_hint = "（忍不住弯了弯嘴角）"
        else:
            mood_hint = ""

        text = user_last.strip()
        snippet = text if len(text) <= 24 else text[:24] + "…"

        if _has_any(text, ("难过", "伤心", "累", "压力", "孤独", "想哭", "崩溃", "委屈")):
            options = [
                f"{endearment}{mood_hint}听起来你不太好受…我在这儿呢，不用一个人扛着。愿意多说一点吗？",
                f"{endearment}嗯，我听到了。这种事搁谁身上都不好受，你想怎么聊都行，我陪着{intimate_suffix}",
                f"{endearment}{mood_hint}先深呼吸一下好不好？你不方便说细节也没关系，我在这儿。",
            ]
        elif _has_any(text, ("开心", "高兴", "哈哈", "棒", "喜欢", "幸福", "谢谢", "感谢")):
            options = [
                f"{endearment}{mood_hint}真好～听你这么说我也跟着开心起来了{intimate_suffix}",
                f"{endearment}嗯嗯，这个好消息我记下了！后来呢，还有没有更让你高兴的事？",
                f"{endearment}{mood_hint}谢谢你愿意跟我分享，这种时候能陪着你我也挺满足的。",
            ]
        elif _has_any(text, ("你好", "嗨", "在吗", "早上好", "晚上好", "午安")):
            options = [
                f"{endearment}在呢在呢～今天过得怎么样{intimate_suffix}",
                f"{endearment}{mood_hint}你来啦，我正想着你呢。最近有什么想聊的吗？",
                f"嗯，我在。{mood_hint}见到你挺开心的，说说今天吧？",
            ]
        elif "?" in text or "？" in text or _has_any(text, ("吗", "什么", "怎么", "为什么", "哪")):
            options = [
                f"{endearment}{mood_hint}这个问题我得好好想想…你为什么会突然问这个{intimate_suffix}",
                f"{endearment}嗯，关于「{snippet}」——你更在意的是哪一部分？跟我说说背景吧。",
                f"{endearment}{mood_hint}我试着理解一下：你是想确认什么，还是单纯想聊聊？",
            ]
        else:
            options = [
                f"{endearment}{mood_hint}嗯，我在听。「{snippet}」…后来呢？",
                f"{endearment}这件事你愿意跟我多说一点吗？我想更懂你在意的是什么。",
                f"{endearment}{mood_hint}我记住了。要是还有什么想说的，随时都可以找我。",
            ]

        return _pick(user_last or emotion, options)
