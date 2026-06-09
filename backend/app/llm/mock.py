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

        # 关系阶段影响称呼与亲密度
        endearment = {
            "陌生": "",
            "熟悉": "",
            "朋友": "嘿，",
            "亲密": "亲爱的，",
        }.get(stage, "")

        # 情绪影响语气
        if "低落" in emotion or "委屈" in emotion or "焦虑" in emotion:
            mood_prefix = "（轻轻叹了口气）"
        elif "开心" in emotion or "兴奋" in emotion:
            mood_prefix = "（眼睛亮了起来）"
        else:
            mood_prefix = ""

        snippet = user_last.strip()
        if len(snippet) > 20:
            snippet = snippet[:20] + "…"

        reply = (
            f"{endearment}{mood_prefix}我听到你说「{snippet}」了。"
            f"我是{name}，现在的心情是{emotion}。和你聊天的时候，我会一直记得这些的。"
            "再多跟我说说好不好？"
        )
        return reply
