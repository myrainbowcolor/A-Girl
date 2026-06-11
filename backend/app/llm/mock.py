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
    m = re.search(r"【你记得关于 ta 的事】\n(.+?)\n\n【回复要求】", system_prompt, re.DOTALL)
    if not m:
        return []
    block = m.group(1).strip()
    if "暂时还没有" in block:
        return []
    return [line.lstrip("- ").strip() for line in block.split("\n") if line.strip().startswith("-")]


def _mood_aside(emotion: str) -> str:
    """情绪驱动的微动作旁白，嵌入句首而非元叙述。"""
    if any(w in emotion for w in ("低落", "委屈", "焦虑")):
        return "嗯……"
    if any(w in emotion for w in ("开心", "兴奋", "满足")):
        return "呀，"
    if "平和" in emotion:
        return ""
    return "嗯，"


def _stage_tone(stage: str) -> tuple[str, str]:
    """关系阶段 → (称呼前缀, 收尾语气)。"""
    return {
        "陌生": ("", "你愿意多跟我说说吗？"),
        "熟悉": ("", "我听着呢，继续说~"),
        "朋友": ("嘿，", "跟我说说细节呗？"),
        "亲密": ("", "我一直都在，你想说什么都行。"),
    }.get(stage, ("", "我在听。"))


def _craft_reply(
    user_text: str,
    emotion: str,
    stage: str,
    name: str,
    memories: list[str],
) -> str:
    """按用户意图与内在状态拼装口语化回复（确定性，无外部模型）。"""
    text = user_text.strip()
    aside = _mood_aside(emotion)
    prefix, closer = _stage_tone(stage)

    # 问候
    if any(w in text for w in ("你好", "嗨", "早上好", "晚上好", "在吗", "哈喽")):
        if stage in ("朋友", "亲密"):
            body = f"{aside}你来啦！今天过得怎么样呀？"
        elif stage == "熟悉":
            body = f"{aside}嗨~ 又见面啦，最近还好吗？"
        else:
            body = f"{aside}你好呀，我是{name}，很高兴认识你。"
        return f"{prefix}{body} {closer}".strip()

    # 情绪低落 — 先共情，少追问
    if any(w in text for w in ("难过", "伤心", "累", "烦", "孤独", "想哭", "崩溃", "压力", "焦虑")):
        if stage in ("朋友", "亲密"):
            body = (
                f"{aside}听起来你真的很不好受……"
                "不用急着解释，我就在这儿陪着你。"
            )
        else:
            body = f"{aside}能感觉到你现在挺难受的，愿意跟我说说发生了什么吗？"
        return f"{prefix}{body}".strip()

    # 感谢
    if any(w in text for w in ("谢谢", "感谢", "多亏")):
        if "开心" in emotion or "满足" in emotion:
            body = "别客气呀，能陪到你我也很开心。"
        else:
            body = "不用谢啦，你愿意跟我说这些，对我来说很重要。"
        return f"{prefix}{body}".strip()

    # 分享开心
    if any(w in text for w in ("开心", "高兴", "棒", "太好了", "哈哈", "喜欢")):
        body = f"{aside}听你这么说我也跟着开心起来了！后来呢？"
        return f"{prefix}{body}".strip()

    # 回忆检索
    if any(w in text for w in ("记得", "还记得", "有没有忘", "叫什么")):
        if memories:
            hint = memories[0]
            if "说：" in hint:
                hint = hint.split("说：", 1)[-1].strip()
            body = f"当然记得呀，{hint}。这件事我一直放在心上呢。"
        else:
            body = "嗯……你之前好像提过，能再提醒我一下吗？我怕记岔了。"
        return f"{prefix}{body}".strip()

    # 问 NPC 状态
    if any(w in text for w in ("你怎么样", "你呢", "在干嘛", "忙吗")):
        mood_hint = {
            "开心又有点小兴奋": "今天心情还不错，有点小雀跃。",
            "平静又满足": "挺好的，安安静静陪着你。",
            "有些焦虑/委屈": "说实话有点替你担心，但见到你就好多了。",
            "低落": "嗯……有点闷闷的，不过跟你聊会好一些。",
        }.get(emotion.split("（")[0], "还行，就是惦记着你。")
        return f"{prefix}{mood_hint} {closer}".strip()

    # 默认：复述关键信息 + 自然延伸（避免"我是xxx心情是xxx"式元叙述）
    snippet = text if len(text) <= 24 else text[:24] + "…"
    if stage in ("朋友", "亲密"):
        body = f"{aside}「{snippet}」——这个我想好好听你说说。"
    else:
        body = f"{aside}嗯，你说「{snippet}」，我在认真听。"
    return f"{prefix}{body} {closer}".strip()


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

        return _craft_reply(user_last, emotion, stage, name, memories)
