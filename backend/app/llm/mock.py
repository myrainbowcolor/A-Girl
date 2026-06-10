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
    """从 system 提示中解析记忆块（persona 格式：- 内容）。"""
    memories: list[str] = []
    in_block = False
    for line in system_prompt.split("\n"):
        if "你记得关于" in line:
            in_block = True
            continue
        if in_block and line.startswith("【"):
            break
        if in_block and line.startswith("- "):
            memories.append(line[2:].strip())
    return memories


def _memory_detail(mem: str) -> str:
    if "ta 说：" in mem:
        return mem.split("ta 说：", 1)[-1].strip()
    return mem.strip()


def _pick_memory(text: str, memories: list[str]) -> str | None:
    """从检索到的记忆中选出与当前问句最相关的一条。"""
    candidates = [_memory_detail(m) for m in memories if m.strip()]
    if not candidates:
        return None
    # 问句里的实词（>=2 字）用于匹配
    keywords = [
        w for w in re.findall(r"[\u4e00-\u9fff]{2,}", text)
        if w not in {"记得", "还记得", "有没有", "什么", "怎么", "为什么", "是不是"}
    ]
    best, best_score = candidates[-1], 0.0
    for detail in candidates:
        score = sum(1.0 for kw in keywords if kw in detail)
        score += sum(0.3 for ch in text if "\u4e00" <= ch <= "\u9fff" and ch in detail)
        if score > best_score:
            best_score = score
            best = detail
    return best if best_score > 0 else candidates[-1]


def _mood_cue(emotion: str) -> str:
    if any(w in emotion for w in ("低落", "委屈", "焦虑")):
        return "（轻轻叹了口气）"
    if any(w in emotion for w in ("开心", "兴奋")):
        return "（眼睛亮了起来）"
    if "满足" in emotion:
        return "（嘴角微微上扬）"
    return ""


def _stage_tone(stage: str) -> tuple[str, str]:
    """返回 (称呼前缀, 句尾语气)。"""
    return {
        "陌生": ("", "呢"),
        "熟悉": ("", "呀"),
        "朋友": ("嘿，", "啦"),
        "亲密": ("亲爱的，", "～"),
    }.get(stage, ("", "呢"))


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

        prefix, tail = _stage_tone(stage)
        mood = _mood_cue(emotion)
        text = user_last.strip()

        reply = self._scenario_reply(text, name, emotion, stage, memories, mood, tail)
        return f"{prefix}{reply}" if prefix else reply

    def _scenario_reply(
        self,
        text: str,
        name: str,
        emotion: str,
        stage: str,
        memories: list[str],
        mood: str,
        tail: str,
    ) -> str:
        """按用户意图选择场景化模板（确定性，便于离线演示）。"""
        low = text.lower()

        # 问候
        if any(w in text for w in ("你好", "嗨", "在吗", "早上好", "中午好", "晚上好", "哈喽")):
            if stage in ("朋友", "亲密"):
                return f"{mood}你来啦！今天过得怎么样{tail}"
            return f"{mood}你好呀，我是{name}，很高兴见到你{tail}"

        # 晚安 / 休息
        if any(w in text for w in ("晚安", "睡觉", "困了", "先睡了", "下线")):
            return f"{mood}晚安，做个好梦。明天想聊的时候，我还在这里等你{tail}"

        # 情绪低落 → 倾听安慰
        if any(w in text for w in ("难过", "伤心", "累", "烦", "孤独", "压力", "焦虑", "崩溃", "想哭", "委屈")):
            snippets = [
                f"{mood}听起来你真的挺不容易的…愿意多跟我说说吗？",
                f"{mood}我在这儿陪着你，不用急着好起来，慢慢来就好。",
                f"{mood}嗯…这种事搁谁身上都不好受，你想哭就哭一会儿也行。",
            ]
            return snippets[len(text) % len(snippets)]

        # 开心分享 → 一起高兴
        if any(w in text for w in ("开心", "高兴", "哈哈", "太好了", "棒", "顺利", "考过了", "成功了")):
            return f"{mood}真的呀！替你开心{tail} 快跟我讲讲怎么回事？"

        # 记忆相关
        if any(w in text for w in ("记得", "还记得", "有没有忘", "叫什么")):
            detail = _pick_memory(text, memories)
            if detail:
                snippet = detail[:24] + ("…" if len(detail) > 24 else "")
                return f"{mood}当然记得呀，你说过「{snippet}」，我一直记着呢。"
            return f"{mood}你跟我说过的事，我都有放在心上。再说一次好不好，我想听得更仔细些{tail}"

        # 想念 / 陪伴
        if any(w in text for w in ("想你", "想念", "陪我", "在不在", "无聊")):
            if stage == "亲密":
                return f"{mood}我也想你{tail} 这会儿能陪你聊天，我觉得挺好的。"
            return f"{mood}在呢在呢，想聊什么都可以，我听着。"

        # 问句 → 认真回应
        if "?" in text or "？" in text or any(w in text for w in ("吗", "呢", "什么", "怎么", "为什么", "哪")):
            snippet = text[:28] + ("…" if len(text) > 28 else "")
            return f"{mood}你问「{snippet}」呀…让我想想。你怎么突然关心这个{tail}"

        # 感谢
        if any(w in text for w in ("谢谢", "感谢", "多亏")):
            return f"{mood}别客气{tail} 能陪着你，我也挺开心的。"

        # 默认：接住话题 + 邀请继续
        snippet = text[:22] + ("…" if len(text) > 22 else "")
        closings = [
            f"嗯嗯，「{snippet}」…我听到了。还想多说一点吗？",
            f"{mood}关于「{snippet}」，我挺在意的。你此刻心情怎么样{tail}",
            f"我在呢。你刚说的「{snippet}」，我想多听几句。",
        ]
        return closings[len(text) % len(closings)]
