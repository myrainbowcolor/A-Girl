"""关键词场景回复引擎（生产路径 scene_first 使用）。

与 llm/mock.py 中的场景分支同源；**不是** pytest 用的 MockLLMProvider。
"""
from __future__ import annotations

from .llm.mock import GENERIC_SCENE_MARKERS, generate_scene_reply


class SceneReplyEngine:
    """规则/场景驱动的 NPC 回复，无大模型调用。"""

    @property
    def name(self) -> str:
        return "scene_engine"

    def generate(self, system_prompt: str, messages: list[dict], temperature: float = 0.8) -> str:
        del temperature  # 确定性场景，不用采样
        return generate_scene_reply(system_prompt, messages)


def is_generic_scene_reply(reply: str) -> bool:
    """未命中具体场景时的问卷式兜底。"""
    return any(m in reply for m in GENERIC_SCENE_MARKERS)
