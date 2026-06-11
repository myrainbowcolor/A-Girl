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


def _snippet(text: str, limit: int = 20) -> str:
    s = text.strip()
    return s if len(s) <= limit else s[:limit] + "…"


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
            "亲密": "亲爱的，",
        }.get(stage, "")

        snippet = _snippet(user_last)
        reply = self._pick_reply(user_last, emotion, stage, name, endearment, snippet)
        return reply

    def _pick_reply(
        self,
        user_last: str,
        emotion: str,
        stage: str,
        name: str,
        endearment: str,
        snippet: str,
    ) -> str:
        """按场景选择拟真回复模板，保持确定性。"""
        text = user_last.strip()

        # 问候
        if any(w in text for w in ("你好", "嗨", "在吗", "早上好", "晚上好", "哈喽")):
            if stage in ("朋友", "亲密"):
                return f"{endearment}来啦来啦～今天怎么样呀？"
            return f"嗯，我在呢。{name}，很高兴见到你。"

        # 用户情绪低落 → 先共情
        if any(w in text for w in ("难过", "伤心", "孤独", "想哭", "崩溃", "压力", "焦虑", "委屈")):
            if "焦虑" in emotion or "委屈" in emotion:
                prefix = "（轻轻叹了口气）"
            else:
                prefix = ""
            if stage in ("朋友", "亲密"):
                return (
                    f"{prefix}{endearment}听到你说这些，我心里也揪了一下。"
                    f"不用急着好起来，我在这儿陪着你，想说就说。"
                )
            return (
                f"{prefix}嗯……听起来你最近不太容易。"
                f"愿意的话，慢慢跟我说说发生了什么？"
            )

        # 用户开心 → 一起高兴
        if any(w in text for w in ("开心", "高兴", "哈哈", "太好了", "棒", "喜欢")):
            if "开心" in emotion or "兴奋" in emotion:
                prefix = "（眼睛亮了起来）"
            else:
                prefix = ""
            if stage in ("朋友", "亲密"):
                return f"{prefix}{endearment}哇，听你这么说我也跟着开心起来了！再多跟我讲讲嘛～"
            return f"{prefix}真好呀，看到你开心我也觉得暖暖的。"

        # 询问记忆
        if any(w in text for w in ("记得", "还记得", "有没有忘", "叫什么")):
            return (
                f"嗯……让我想想。"
                f"你之前跟我提过「{snippet}」这件事，我一直记着呢。"
            )

        # 道别
        if any(w in text for w in ("晚安", "再见", "拜拜", "先走了", "睡了")):
            if stage in ("朋友", "亲密"):
                return f"{endearment}好呀，早点休息～做个好梦，明天再来找我聊。"
            return "嗯，晚安。好好休息，下次见。"

        # 默认：情绪与关系影响语气
        if "低落" in emotion or "委屈" in emotion or "焦虑" in emotion:
            mood_prefix = "（轻声）"
        elif "开心" in emotion or "兴奋" in emotion:
            mood_prefix = "（笑）"
        else:
            mood_prefix = ""

        if stage in ("朋友", "亲密"):
            return (
                f"{endearment}{mood_prefix}嗯，我听到你说「{snippet}」了。"
                f"跟我说说更多吧，我想听。"
            )
        return (
            f"{mood_prefix}我听到你说「{snippet}」了。"
            f"我是{name}，现在的心情是{emotion}。"
            f"和你聊天的时候，我会一直记得这些的。再多跟我说说好不好？"
        )
