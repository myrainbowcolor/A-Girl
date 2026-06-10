"""离线 Mock Provider。

不依赖外部 API，根据 system 提示中的情绪/关系线索与用户最后一句话，
生成有"人味"且能体现内部状态的确定性回复，便于无 Key 环境下验证整条编排链路。
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


def _pick_variant(options: list[str], seed: str) -> str:
    if not options:
        return ""
    idx = int(hashlib.md5(seed.encode("utf-8")).hexdigest(), 16) % len(options)
    return options[idx]


def _clean_memory(mem: str) -> str:
    """去掉记忆存储前缀，保留用户原话感。"""
    if mem.startswith("ta 说："):
        return mem[4:].strip()
    return mem.strip()


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

        # 关系阶段影响称呼与亲密度
        endearment = {
            "陌生": "",
            "熟悉": "",
            "朋友": "嘿，",
            "亲密": "嗯，",
        }.get(stage, "")

        text = user_last.strip()
        seed = f"{text}|{emotion}|{stage}"

        # 情绪影响语气前缀（轻量舞台指示，模拟真人神态）
        if any(k in emotion for k in ("低落", "委屈", "焦虑")):
            mood_prefix = "嗯…"
        elif any(k in emotion for k in ("开心", "兴奋", "雀跃")):
            mood_prefix = "哈哈，"
        elif "惊讶" in emotion:
            mood_prefix = "诶？"
        else:
            mood_prefix = ""

        # 按用户输入意图分支，生成更拟真的短回复
        reply_body = self._reply_body(text, emotion, stage, memories, seed)

        return f"{endearment}{mood_prefix}{reply_body}".strip()

    def _reply_body(
        self,
        text: str,
        emotion: str,
        stage: str,
        memories: list[str],
        seed: str,
    ) -> str:
        """根据用户话茬生成 1~2 句口语化回复。"""
        if not text:
            return _pick_variant(["在呢，怎么啦？", "嗯，我听着呢。"], seed)

        # 问候
        if re.search(r"^(你好|嗨|哈喽|早上好|晚上好|在吗)", text):
            return _pick_variant([
                "在呀～今天过得怎么样？",
                "嗯，在呢。想聊点什么？",
                "你好呀，见到你挺开心的。",
            ], seed)

        # 感谢
        if any(w in text for w in ("谢谢", "感谢", "多亏")):
            return _pick_variant([
                "不用客气啦，能陪着你我也挺开心的。",
                "嘿嘿，跟我还这么客气呀。",
                "应该的嘛，你愿意跟我说这些，我也很高兴。",
            ], seed)

        # 负面情绪：先共情
        if any(w in text for w in ("难过", "伤心", "累", "烦", "孤独", "压力", "焦虑", "想哭", "崩溃")):
            empathy = _pick_variant([
                "听起来你最近真的挺不容易的…我在呢，慢慢说。",
                "嗯，我懂那种感觉。不想说太多也没关系，我陪着你。",
                "抱抱你。这种事搁谁身上都不好受，你想从哪说起？",
            ], seed)
            if memories:
                raw = _clean_memory(memories[0])
                mem_hint = raw[:18] + ("…" if len(raw) > 18 else "")
                return f"{empathy} 我还记得你说过{mem_hint}，现在还好吗？"
            return empathy

        # 开心分享
        if any(w in text for w in ("开心", "高兴", "哈哈", "太好了", "顺利", "棒")):
            return _pick_variant([
                "真好呀！快跟我说说，我也跟着高兴～",
                "嘿嘿，听你这么说我也心情变好了。",
                "哇，那太棒了！后来呢？",
            ], seed)

        # 询问记忆
        if any(w in text for w in ("记得", "还记得", "有没有忘")):
            for mem in memories:
                if any(k in mem for k in ("猫", "橘子", "名字", "生日", "工作", "考试")):
                    snippet = _clean_memory(mem)[:30]
                    return _pick_variant([
                        f"当然记得呀，{snippet}。",
                        f"嗯嗯，这事我记着——{snippet}。",
                    ], seed)
            return _pick_variant([
                "你跟我说过的事，我都有认真记着。",
                "嗯…让我想想，你再多提醒我一下？",
            ], seed)

        # 想念
        if any(w in text for w in ("想你", "想念", "好久不见")):
            closeness = "我也挺想你的。" if stage in ("朋友", "亲密") else "好久没见你啦。"
            return _pick_variant([
                f"{closeness} 最近还好吗？",
                f"嗯，{closeness}",
            ], seed)

        # 默认：接住话茬 + 轻追问（避免机械复述整句）
        snippet = text if len(text) <= 24 else text[:22] + "…"
        tail = _pick_variant([
            "嗯，我听到了。后来呢？",
            "是这样呀…再多跟我说一点？",
            "我懂。那现在你心里感觉怎么样？",
            "嗯嗯，然后呢？",
        ], seed)
        if stage == "亲密":
            tail = _pick_variant([
                "嗯，我在听。你愿意多说一点吗？",
                "我懂你的意思…现在感觉好点了吗？",
            ], seed)
        return f"「{snippet}」——{tail}"
