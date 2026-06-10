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


def _extract_memories(system_prompt: str) -> list[str]:
    """从 system 提示中解析检索到的记忆条目。"""
    m = re.search(r"【你记得关于 ta 的事】\n(.*?)\n\n【", system_prompt, re.DOTALL)
    if not m:
        return []
    block = m.group(1).strip()
    if "暂时还没有" in block:
        return []
    return [line[2:].strip() for line in block.split("\n") if line.startswith("- ")]


def _user_tone(text: str) -> str:
    """粗分用户话语意图，驱动更拟真的回复模板。"""
    t = text.strip()
    if any(w in t for w in ("你好", "嗨", "哈喽", "在吗", "早上好", "晚上好")):
        return "greet"
    if "?" in t or "？" in t or any(w in t for w in ("吗", "呢", "什么", "怎么", "为什么", "哪")):
        return "question"
    if any(w in t for w in ("难过", "伤心", "累", "烦", "孤独", "压力", "焦虑", "崩溃", "哭", "不开心", "委屈")):
        return "negative"
    if any(w in t for w in ("开心", "高兴", "喜欢", "谢谢", "棒", "哈哈", "幸福", "温暖")):
        return "positive"
    if any(w in t for w in ("我", "今天", "刚才", "最近")) and len(t) >= 8:
        return "share"
    return "neutral"


def _memory_hook(memories: list[str], user_text: str) -> str:
    """若记忆与用户话有词重叠，抽一句自然引用。"""
    if not memories:
        return ""
    user_chars = set(user_text)
    best, best_score = "", 0
    for mem in memories:
        overlap = sum(1 for ch in mem if ch in user_chars and len(ch.strip()) > 0)
        if overlap > best_score:
            best_score, best = overlap, mem
    if best_score < 2:
        return ""
    # 去掉 "ta 说：" 前缀，让引用更口语
    snippet = best.replace("ta 说：", "").strip()
    if len(snippet) > 24:
        snippet = snippet[:24] + "…"
    return f"对了，我还记得你提过「{snippet}」。"


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
        memories = _extract_memories(system_prompt)
        tone = _user_tone(user_last)
        mem_hook = _memory_hook(memories, user_last)

        endearment = {
            "陌生": "",
            "熟悉": "",
            "朋友": "嘿，",
            "亲密": "",
        }.get(stage, "")
        close_suffix = "嗯，我在呢。" if stage == "亲密" else ""

        # 情绪影响语气小动作（与 EmotionState.label 关键词对齐）
        if any(w in emotion for w in ("低落", "委屈", "焦虑")):
            mood_act = "（轻轻叹了口气）"
        elif any(w in emotion for w in ("开心", "兴奋", "满足", "暖")):
            mood_act = "（忍不住笑了一下）"
        elif "惊讶" in emotion or "好奇" in emotion:
            mood_act = "（眼睛微微睁大）"
        else:
            mood_act = ""

        snippet = user_last.strip()
        if len(snippet) > 28:
            snippet = snippet[:28] + "…"

        if tone == "greet":
            body = f"在呀，我是{name}～{mood_act}今天怎么样？"
        elif tone == "negative":
            body = (
                f"{mood_act}听你这么说，我心里也揪了一下。"
                f"「{snippet}」——你愿意多跟我说说吗？不用急着整理好情绪。"
            )
        elif tone == "positive":
            body = (
                f"{mood_act}真好呀，听你讲「{snippet}」我也跟着开心起来了。"
                f"这种时候就想多听你多说两句～"
            )
        elif tone == "question":
            body = (
                f"{mood_act}你问的这个我认真想了想——"
                f"关于「{snippet}」，我更想先听听你心里是怎么想的？"
            )
        elif tone == "share":
            body = (
                f"{mood_act}嗯嗯，我在听。"
                f"「{snippet}」这件事，感觉对你挺重要的吧？"
            )
        else:
            body = (
                f"{mood_act}我听到了，你说的是「{snippet}」。"
                f"我现在心情是{emotion}，跟你聊着聊着就会一直记得的。"
            )

        tail = {
            "陌生": " 我们慢慢熟悉～",
            "熟悉": " 有什么都可以跟我聊。",
            "朋友": " 随时找我呀。",
            "亲密": f" {close_suffix}",
        }.get(stage, "")

        reply = f"{endearment}{body}"
        if mem_hook and tone != "greet":
            reply += mem_hook
        reply += tail
        return reply.strip()
