"""离线 Mock Provider。

不依赖外部 API，根据 system 提示中的情绪/关系/记忆线索与用户输入，
生成有"人味"且能体现内在状态的确定性回复，便于无 Key 环境下验证整条编排链路。
"""
from __future__ import annotations

import hashlib
import re

from .base import LLMProvider


def _extract(tag: str, text: str, default: str = "") -> str:
    m = re.search(rf"{tag}：(.+)", text)
    return m.group(1).strip() if m else default


def _extract_memories(system_prompt: str) -> list[str]:
    """从 system 提示中解析检索到的记忆条目。"""
    block = re.search(r"【你记得关于 ta 的事】\n([\s\S]*?)\n\n【回复要求】", system_prompt)
    if not block:
        return []
    lines = [ln.strip()[2:] for ln in block.group(1).splitlines() if ln.strip().startswith("- ")]
    return [ln for ln in lines if ln and "暂时还没有" not in ln]


def _seed(*parts: str) -> int:
    return int(hashlib.md5("".join(parts).encode("utf-8")).hexdigest(), 16)


def _pick(seed: int, options: list[str]) -> str:
    return options[seed % len(options)]


def _classify_intent(text: str) -> str:
    t = text.strip()
    if not t:
        return "neutral"
    if any(w in t for w in ("你好", "嗨", "哈喽", "早上好", "晚上好", "在吗", "在不在")):
        return "greeting"
    if any(w in t for w in ("再见", "拜拜", "晚安", "先走了", "下次聊")):
        return "farewell"
    if any(w in t for w in ("记得", "还记得", "有没有忘", "叫什么")):
        return "recall"
    if "?" in t or "？" in t or any(w in t for w in ("什么", "怎么", "为什么", "哪", "谁", "几", "吗")):
        return "question"
    if any(w in t for w in ("难过", "伤心", "累", "烦", "孤独", "压力", "焦虑", "崩溃", "哭", "不开心", "想哭", "绝望")):
        return "sadness"
    if any(w in t for w in ("开心", "高兴", "喜欢", "谢谢", "感谢", "哈哈", "棒", "幸福", "温暖")):
        return "happiness"
    return "sharing"


def _mood_tone(emotion: str) -> str:
    if any(w in emotion for w in ("低落", "委屈", "焦虑")):
        return "soft"
    if any(w in emotion for w in ("开心", "兴奋", "满足")):
        return "bright"
    return "calm"


def _endearment(stage: str) -> str:
    return {
        "陌生": "",
        "熟悉": "",
        "朋友": "嘿，",
        "亲密": "",
    }.get(stage, "")


def _nickname(stage: str, name: str) -> str:
    if stage == "亲密":
        return _pick(_seed(stage, name), ["", "呀，"])
    if stage == "朋友":
        return _pick(_seed(name, stage), ["", "嗯，"])
    return ""


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

        intent = _classify_intent(user_last)
        tone = _mood_tone(emotion)
        seed = _seed(user_last, emotion, stage, str(len(memories)))
        prefix = _endearment(stage) + _nickname(stage, name)

        reply = self._compose(
            intent=intent, tone=tone, prefix=prefix, name=name,
            user_text=user_last.strip(), memories=memories, seed=seed, stage=stage,
        )
        return reply

    def _compose(
        self,
        *,
        intent: str,
        tone: str,
        prefix: str,
        name: str,
        user_text: str,
        memories: list[str],
        seed: int,
        stage: str,
    ) -> str:
        snippet = user_text
        if len(snippet) > 24:
            snippet = snippet[:24] + "…"

        mem_hint = ""
        if memories:
            mem_hint = memories[seed % len(memories)]
            if len(mem_hint) > 30:
                mem_hint = mem_hint[:30] + "…"

        if intent == "greeting":
            opts = [
                f"{prefix}你好呀，我是{name}，很高兴见到你~",
                f"{prefix}嗨，在呢在呢，今天想聊点什么？",
                f"{prefix}你好~ 我刚好也在，陪你聊聊天吧。",
            ]
            if stage in ("朋友", "亲密"):
                opts.append(f"{prefix}你来啦，我正想着你呢。")
            return _pick(seed, opts)

        if intent == "farewell":
            opts = [
                f"{prefix}好呀，晚安，做个好梦~",
                f"{prefix}嗯，那先休息吧，记得照顾好自己哦。",
                f"{prefix}拜拜，下次再来找我聊呀。",
            ]
            if tone == "bright":
                opts.append(f"{prefix}今天聊得很开心，下次见~")
            return _pick(seed, opts)

        if intent == "recall" and memories:
            if "猫" in user_text or "橘子" in user_text:
                for m in memories:
                    if "橘子" in m or "猫" in m:
                        return _pick(seed, [
                            f"{prefix}当然记得呀，你说过橘子对不对？它一定很可爱吧。",
                            f"{prefix}嗯嗯，是橘子对吧？你那么喜欢它，我都记着呢。",
                        ])
            return _pick(seed, [
                f"{prefix}记得的，{mem_hint}，这些我都放在心里了。",
                f"{prefix}没忘呢，你之前说过{mem_hint}，我一直都记着。",
            ])

        if intent == "sadness":
            opts = [
                f"{prefix}听起来你不太好受……想多说一点吗？我在这儿听着呢。",
                f"{prefix}嗯……抱抱你。不用急着好起来，慢慢来就好。",
                f"{prefix}我能感觉到你心里沉甸甸的，愿意跟我说说发生了什么吗？",
            ]
            if tone == "soft":
                opts.append(f"{prefix}我也跟着有点揪心……你别一个人扛着，好吗？")
            if stage in ("朋友", "亲密"):
                opts.append(f"{prefix}看到你难过，我也会心疼的。不管怎样，我都在。")
            return _pick(seed, opts)

        if intent == "happiness":
            opts = [
                f"{prefix}哇，听你这么说我也跟着开心起来了~",
                f"{prefix}真好呀，这种好心情值得好好记住！",
                f"{prefix}嘿嘿，你开心的样子我都能想象到呢。",
            ]
            if tone == "bright":
                opts.append(f"{prefix}太棒了！快跟我多说说，是什么让你这么高兴？")
            return _pick(seed, opts)

        if intent == "question":
            opts = [
                f"{prefix}这个问题……我想想，{snippet}，你是想了解哪方面呢？",
                f"{prefix}嗯，关于「{snippet}」，你怎么想的？我也想听听你的想法。",
                f"{prefix}我不太敢随便下结论，但我很愿意陪你一起琢磨这件事。",
            ]
            return _pick(seed, opts)

        # sharing / neutral — 引用记忆或自然接话
        if memories and seed % 3 == 0:
            return _pick(seed, [
                f"{prefix}嗯，{snippet}……对了，我还记得{mem_hint}，跟这个有关系吗？",
                f"{prefix}我在听呢。你刚说的让我想起{mem_hint}。",
            ])

        opts = [
            f"{prefix}嗯，{snippet}……然后呢？我想多了解一点。",
            f"{prefix}我在认真听哦，你继续说，我不着急。",
            f"{prefix}原来是这样呀，谢谢你愿意跟我说这些。",
        ]
        if stage == "陌生":
            opts = [
                f"{prefix}嗯，{snippet}……谢谢你愿意跟我分享。",
                f"{prefix}我在听呢，你慢慢说就好。",
            ]
        if tone == "soft":
            opts.append(f"{prefix}轻轻叹了口气……没事的，我陪着你。")
        elif tone == "bright":
            opts.append(f"{prefix}听起来不错诶，再多跟我说说？")
        return _pick(seed, opts)
