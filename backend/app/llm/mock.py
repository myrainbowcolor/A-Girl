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
    m = re.search(r"【你记得关于 ta 的事】\n(.+?)\n\n【回复要求】", system_prompt, re.S)
    if not m:
        return []
    block = m.group(1).strip()
    if "暂时还没有" in block:
        return []
    return [line.lstrip("- ").strip() for line in block.splitlines() if line.strip().startswith("-")]


def _pick_memory_snippet(memories: list[str]) -> str:
    """从记忆里挑一句可自然引用的片段。"""
    if not memories:
        return ""
    raw = memories[0]
    # 去掉「ta 说：」前缀，保留用户原话感
    if raw.startswith("ta 说："):
        raw = raw[4:]
    if len(raw) > 24:
        raw = raw[:24] + "…"
    return raw


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
        mem_snip = _pick_memory_snippet(memories)

        endearment = {
            "陌生": "",
            "熟悉": "",
            "朋友": "嘿，",
            "亲密": "亲爱的，",
        }.get(stage, "")

        # 情绪影响语气前缀（与 label() 关键词对齐，供测试链路识别）
        if any(k in emotion for k in ("低落", "委屈", "焦虑")):
            mood_prefix = "（轻轻叹了口气）"
        elif any(k in emotion for k in ("开心", "兴奋", "满足")):
            mood_prefix = "（眼睛亮了起来）"
        else:
            mood_prefix = ""

        text = user_last.strip()

        # 按用户意图分支，生成更拟真的短回复
        if any(w in text for w in ("你好", "嗨", "在吗", "哈喽", "早上好", "晚上好")):
            if stage in ("朋友", "亲密"):
                body = f"在呢在呢～今天怎么样呀？"
            else:
                body = f"你好呀，我是{name}，很高兴见到你～"
        elif any(w in text for w in ("难过", "伤心", "孤独", "想哭", "崩溃", "好累", "压力")):
            body = "听起来你最近挺不容易的…我就在这儿，你愿意多说一点吗？不用急着把一切都讲清楚。"
        elif any(w in text for w in ("谢谢", "感谢", "多亏")):
            body = "别客气呀，能陪你说说话我也挺开心的。"
        elif "?" in text or "？" in text or any(w in text for w in ("吗", "么", "什么", "怎么", "为什么")):
            if mem_snip:
                body = f"嗯…你上次提过「{mem_snip}」，我记着这件事呢。你具体想问哪一部分？"
            else:
                body = "嗯，让我想想…你愿意再跟我多说一点背景吗？这样我能更懂你问的是什么。"
        elif any(w in text for w in ("开心", "高兴", "喜欢", "棒", "哈哈")):
            body = "听你这么说我也跟着开心起来了！后来呢，还有什么好玩的事吗？"
        else:
            snippet = text if len(text) <= 22 else text[:22] + "…"
            if mem_snip:
                body = (
                    f"我听到你说「{snippet}」了。"
                    f"对了，我还记得你提过「{mem_snip}」——这件事后来怎么样了？"
                )
            else:
                body = f"我听到你说「{snippet}」了。嗯，我在听，你慢慢说。"

        reply = f"{endearment}{mood_prefix}{body}"
        return reply
