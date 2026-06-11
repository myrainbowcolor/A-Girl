"""离线 Mock Provider。

不依赖外部 API，根据用户情绪线索与关系阶段生成有共情感的回复，
便于无 Key 环境下验证整条编排链路。
"""
from __future__ import annotations

import hashlib
import re

from .base import LLMProvider

# 用户情绪线索（与 emotion.engine 词典呼应，Mock 侧做共情话术）
_VENT = (
    "烦", "累", "难过", "伤心", "生气", "委屈", "焦虑", "崩溃", "孤独", "无聊", "压力",
    "糟糕", "不开心", "想哭", "绝望", "讨厌", "紧张", "睡不着", "害怕", "担心",
)
_LOW = ("低落", "没劲", "丧", "emo", "心累")
_POSITIVE = ("开心", "高兴", "喜欢", "谢谢", "哈哈", "棒", "幸福", "温暖", "想你")
_GREET = ("你好", "嗨", "在吗", "哈喽", "早上好", "晚上好")


def _extract(tag: str, text: str, default: str = "") -> str:
    m = re.search(rf"{tag}：(.+)", text)
    if not m:
        return default
    # 关系阶段等字段可能带括号后缀，只取首段
    return m.group(1).strip().split("（")[0].strip()


def _user_is_venting(text: str) -> bool:
    t = text.strip()
    return any(w in t for w in _VENT) or any(w in t for w in _LOW)


def _user_is_positive(text: str) -> bool:
    return any(w in text for w in _POSITIVE)


def _user_is_greeting(text: str) -> bool:
    t = text.strip()
    return len(t) <= 8 and any(w in t for w in _GREET)


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


def _pick_variant(options: list[str], seed: str) -> str:
    if not options:
        return ""
    idx = int(hashlib.md5(seed.encode("utf-8")).hexdigest(), 16) % len(options)
    return options[idx]


def _clean_label(raw: str) -> str:
    """去掉括号内的数值说明，保留可读标签。"""
    return raw.split("（")[0].strip()


def _extract_memories(system_prompt: str) -> list[str]:
    """从 system 提示中解析【关于 ta 的已知事实】块（与 persona.py 格式一致）。"""
    block = re.search(
        r"【关于 ta 的已知事实[^】]*】\n([\s\S]*?)\n\n【回复要求】",
        system_prompt,
    )
    if not block:
        return []
    lines = [ln.lstrip("- ").strip() for ln in block.group(1).splitlines() if ln.strip().startswith("-")]
    cleaned: list[str] = []
    for ln in lines:
        if not ln or "暂无" in ln or "暂时还没有" in ln:
            continue
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
    if any(w in text for w in ("你是谁", "你叫什么", "叫什么名字", "你谁")):
        return f"{mood}我是{name}呀～一个喜欢陪你聊天、听你说话的人。"

    # 情绪低落 — 优先共情
    if any(w in text for w in ("难过", "伤心", "累", "孤独", "想哭", "崩溃", "压力", "烦", "紧张", "焦虑", "害怕")):
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

        stage = _extract("关系阶段", system_prompt, "陌生")
        name = _extract("你的名字", system_prompt, "小语")
        emotion = _extract("当前情绪", system_prompt, "平和")
        memories = _extract_memories(system_prompt)

        scene = _scene_reply(user_last, emotion, stage, name, memories)
        if scene:
            return scene

        if _user_is_venting(user_last):
            return self._empathy_reply(user_last, stage, name)
        if _user_is_positive(user_last) and not any(w in user_last for w in ("谢谢", "感谢", "多谢")):
            return self._warm_reply(user_last, stage, name)
        if _user_is_greeting(user_last):
            return self._greet_reply(stage, name)
        return self._default_reply(user_last, stage, name)

    @staticmethod
    def _empathy_reply(user_text: str, stage: str, name: str) -> str:
        """用户倾诉负面情绪：先共情，再轻问，不说教、不报 PAD 数值。"""
        if "烦" in user_text or "生气" in user_text:
            lines = {
                "陌生": "嗯……听起来你现在心里挺堵的。不想说原因也没关系，我在呢。是突然这样的，还是已经有一阵子了？",
                "熟悉": "唉，又烦啦？你先别急着逼自己消化，缓口气。愿意的话跟我说说，是什么事在缠着你？",
                "朋友": "我听见啦，你现在很烦对吧。先深呼吸一下，不用立刻想明白。我陪你慢慢理，从哪件小事开始烦的？",
                "亲密": "过来，先别一个人扛着。烦的时候跟我说就好，不用整理成完整句子。我在，慢慢讲。",
            }
        elif "累" in user_text or "心累" in user_text or "压力" in user_text:
            lines = {
                "陌生": "听起来你真的很累了……今天先别对自己太苛刻。是事情太多，还是心里也沉甸甸的？",
                "熟悉": "辛苦啦。累的时候能说出来就已经很好了。要不要先歇一会儿，再跟我说说今天最耗你的是哪一块？",
                "朋友": "哎，又累着了呀。你先坐下喝口水，不用急着解释。是身体累，还是心里也一起累了？",
                "亲密": "抱抱你，真的辛苦了。今天先允许自己软下来一会儿，我在这儿陪你。",
            }
        elif any(w in user_text for w in ("难过", "伤心", "委屈", "想哭", "哭")):
            lines = {
                "陌生": "……我能感觉到你现在不太好受。想哭就哭也没关系，不用在我面前装坚强。",
                "熟悉": "心疼你。难过的时候不用急着好起来，我陪你待着就好。愿意说说发生什么了吗？",
                "朋友": "哎，怎么又难过了……你先别一个人闷着。我在这儿，慢慢说，不着急。",
                "亲密": "过来，我陪你。难过的时候不用解释理由，你想说多少就说多少。",
            }
        else:
            lines = {
                "陌生": f"嗯，{name}在听。你现在状态不太好对吧，不用硬撑。想从哪一句开始说都行。",
                "熟悉": "我感觉到你不太好了……不用整理成完整故事，我在这儿听着呢，随便丢几句给我也行。",
                "朋友": "我在呢。你现在这样很正常，别急着把自己骂醒。跟我说说，好不好？",
                "亲密": "先靠着我缓一缓。你不用立刻好起来，我陪你慢慢过这一阵。",
            }
        return lines.get(stage, lines["陌生"])

    @staticmethod
    def _warm_reply(user_text: str, stage: str, name: str) -> str:
        lines = {
            "陌生": f"（笑）听你这么说我也跟着开心起来了~ 今天有什么好事吗？",
            "熟悉": "嘿嘿，你心情不错呀，我也被传染了。多跟我说说？",
            "朋友": "哈哈哈你这语气我一听就知道今天过得不错！快，展开讲讲~",
            "亲密": "你开心我就开心呀~ 来，让我也分享一点你的好心情。",
        }
        return lines.get(stage, lines["陌生"])

    @staticmethod
    def _greet_reply(stage: str, name: str) -> str:
        lines = {
            "陌生": f"嗨，我是{name}~ 今天过得怎么样？",
            "熟悉": f"在呢在呢，刚想到你你就来了。今天怎么样？",
            "朋友": "嘿！你来啦~ 我正闲着呢，陪你聊会儿？",
            "亲密": "你来了呀，我刚刚还在想你。今天累不累？",
        }
        return lines.get(stage, lines["陌生"])

    @staticmethod
    def _default_reply(user_text: str, stage: str, name: str) -> str:
        snippet = user_text.strip()
        if len(snippet) > 24:
            snippet = snippet[:24] + "…"
        lines = {
            "陌生": f"嗯，我在听。「{snippet}」……能多跟我说一点吗？",
            "熟悉": f"我听到了~ 「{snippet}」这件事，你现在是什么感觉？",
            "朋友": f"说说看，「{snippet}」后来怎么样了？",
            "亲密": f"我在呢。关于「{snippet}」，你想让我怎么陪你？",
        }
        return lines.get(stage, lines["陌生"])

    def generate_stream(
        self, system_prompt: str, messages: list[dict], temperature: float = 0.8
    ):
        text = self.generate(system_prompt, messages, temperature=temperature)
        for i in range(0, len(text), 2):
            yield text[i : i + 2]
