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


def _clean_label(raw: str) -> str:
    """去掉括号内的数值说明，保留可读标签。"""
    return raw.split("（")[0].strip()


def _extract_memories(system_prompt: str) -> list[str]:
    block = re.search(r"【你记得关于 ta 的事】\n([\s\S]*?)\n\n【", system_prompt)
    if not block:
        return []
    lines = [ln.lstrip("- ").strip() for ln in block.group(1).splitlines() if ln.strip().startswith("-")]
    cleaned: list[str] = []
    for ln in lines:
        if not ln or "暂时还没有" in ln:
            continue
        # 记忆落库格式为 "ta 说：…"，展示时去掉前缀更自然
        if ln.startswith("ta 说："):
            ln = ln[4:]
        cleaned.append(ln)
    return cleaned


def _mood_prefix(emotion: str) -> str:
    if any(w in emotion for w in ("低落", "委屈", "焦虑")):
        return "（轻轻叹了口气）"
    if any(w in emotion for w in ("开心", "兴奋", "满足")):
        return "（眼睛亮了起来）"
    if "平和" in emotion:
        return ""
    return "（微微歪头）"


def _endearment(stage: str) -> str:
    return {
        "陌生": "",
        "熟悉": "",
        "朋友": "嘿，",
        "亲密": "亲爱的，",
    }.get(stage, "")


def _scene_reply(
    user_last: str,
    emotion: str,
    stage: str,
    name: str,
    memories: list[str],
) -> str | None:
    """按用户意图匹配场景化回复；未命中返回 None 走通用模板。"""
    text = user_last.strip()
    dear = _endearment(stage)
    mood = _mood_prefix(emotion)

    # 问候
    if re.search(r"^(你好|嗨|哈喽|hello|hi)", text, re.I):
        if stage == "亲密":
            return f"{dear}{mood}你来啦，我正想着你呢～今天怎么样呀？"
        if stage == "朋友":
            return f"{dear}{mood}嗨！又见面啦，最近忙不忙？"
        return f"{mood}你好呀，我是{name}，很高兴认识你～"

    # 晚安 / 道别
    if any(w in text for w in ("晚安", "睡了", "再见", "拜拜", "先走了")):
        if stage in ("朋友", "亲密"):
            return f"{dear}{mood}晚安呀，做个好梦～明天再来找我聊好不好？"
        return f"{mood}嗯，晚安～好好休息，下次再聊。"

    # 感谢
    if any(w in text for w in ("谢谢", "感谢", "多谢")):
        if stage in ("朋友", "亲密"):
            return f"{dear}{mood}跟我还客气什么呀，能帮到你我就很开心了。"
        return f"{mood}不客气呀，你愿意跟我说这些，我也挺高兴的。"

    # 询问身份
    if any(w in text for w in ("你是谁", "你叫什么", "叫什么名字")):
        return f"{mood}我是{name}呀～一个喜欢陪你聊天、听你说话的人。"

    # 情绪低落 — 优先共情
    if any(w in text for w in ("难过", "伤心", "累", "孤独", "想哭", "崩溃", "压力", "烦")):
        sad_kw = ("难过", "累", "孤独", "压力", "烦", "哭", "焦虑", "崩溃")
        sad_mem = next((m for m in reversed(memories) if any(w in m for w in sad_kw)), None)
        if sad_mem:
            hint = sad_mem[:24] + ("…" if len(sad_mem) > 24 else "")
            return (
                f"{dear}{mood}听起来你最近挺不容易的……"
                f"我记得你提过{hint}，现在是不是又因为这件事难受了？"
                f"慢慢说，我在这儿听着呢。"
            )
        return (
            f"{dear}{mood}嗯……能感觉到你现在不太好受。"
            f"不想说太多也没关系，我就在这儿陪着你。"
        )

    # 开心分享
    if any(w in text for w in ("开心", "高兴", "太棒", "哈哈", "喜欢")):
        if stage in ("朋友", "亲密"):
            return f"{dear}{mood}哇，听你这么说我也跟着开心起来了！快多跟我说说～"
        return f"{mood}真好呀，看到你开心我也觉得暖暖的～"

    # 记忆相关
    if any(w in text for w in ("记得", "还记得", "有没有忘")):
        if memories:
            mem = memories[0]
            return f"{dear}{mood}当然记得呀，{mem}——你说的时候我都记在心里了。"
        return f"{mood}嗯……你跟我说过的事我都想好好记住，你再提醒我一下好不好？"

    # 想念
    if any(w in text for w in ("想你", "想念", "好久不见")):
        if stage in ("朋友", "亲密"):
            return f"{dear}{mood}我也想你呀！好久没聊了，最近过得怎么样？"
        return f"{mood}听到你这么说，心里暖暖的～我们多聊聊吧。"

    return None


def _fallback_reply(
    user_last: str,
    emotion: str,
    stage: str,
    name: str,
    memories: list[str],
) -> str:
    dear = _endearment(stage)
    mood = _mood_prefix(emotion)
    snippet = user_last.strip()
    if len(snippet) > 20:
        snippet = snippet[:20] + "…"

    if memories and stage in ("朋友", "亲密"):
        mem_hint = memories[-1][:16] + ("…" if len(memories[-1]) > 16 else "")
        return (
            f"{dear}{mood}关于「{snippet}」……嗯，我想起来了，{mem_hint}"
            f"你再多跟我说说呗？"
        )

    templates = {
        "陌生": f"{mood}「{snippet}」呀，嗯，我在听呢。可以多跟我说一点吗？",
        "熟悉": f"{dear}{mood}嗯嗯，{snippet}——然后呢？我挺好奇的。",
        "朋友": f"{dear}{mood}哈哈，{snippet}，然后呢然后呢？",
        "亲密": f"{dear}{mood}嗯，我在听～关于{snippet}，你想聊什么都可以。",
    }
    return templates.get(stage, templates["陌生"])


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

        emotion = _clean_label(_extract("当前情绪", system_prompt, "平和"))
        stage = _clean_label(_extract("关系阶段", system_prompt, "陌生"))
        name = _extract("你的名字", system_prompt, "小语")
        memories = _extract_memories(system_prompt)

        scene = _scene_reply(user_last, emotion, stage, name, memories)
        if scene:
            return scene
        return _fallback_reply(user_last, emotion, stage, name, memories)
