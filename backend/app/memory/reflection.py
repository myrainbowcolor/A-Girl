"""LLM 驱动的记忆反思与归纳。"""
from __future__ import annotations

from ..domain import MemoryType, Persona
from ..llm.base import LLMProvider
from .store import MemoryStore


def fallback_reflection(memories: list[str]) -> str:
    joined = "；".join(memories[:8])
    return f"对最近互动的总结：{joined}"


def llm_reflection(
    llm: LLMProvider,
    persona: Persona,
    memory_lines: list[str],
    relationship_summary: str = "",
) -> str:
    mem_block = "\n".join(f"- {m}" for m in memory_lines[:10])
    system = (
        f"你是{persona.name}的内心反思模块。根据下列**已发生**的对话记忆，"
        "用1-3句中文提炼：用户最近的状态、我在意什么、下次聊天可以注意什么。"
        "禁止编造记忆中没有的信息。不要列表，不要 JSON。"
    )
    extra = f"\n当前关系归纳：{relationship_summary}" if relationship_summary else ""
    user = f"记忆：\n{mem_block}{extra}"
    try:
        text = llm.generate(system, [{"role": "user", "content": user}], temperature=0.4)
        text = text.strip().split("\n")[0][:200]
        return text if len(text) >= 8 else fallback_reflection(memory_lines)
    except Exception:
        return fallback_reflection(memory_lines)


def maybe_reflect(
    memory: MemoryStore,
    user_id: str,
    every_n: int,
    llm: LLMProvider | None,
    persona: Persona,
    relationship_summary: str = "",
) -> str | None:
    """累计 N 条记忆时生成反思，返回洞察文本（若触发）。"""
    if every_n <= 0:
        return None
    count = memory.count(user_id)
    if count == 0 or count % every_n != 0:
        return None
    recent = memory.retrieve(user_id, "最近发生的事和 ta 的状态", top_k=every_n)
    lines = [m.content for m in recent]
    if llm is not None and llm.name != "mock":
        insight = llm_reflection(llm, persona, lines, relationship_summary)
    else:
        insight = fallback_reflection(lines)
    memory.add(user_id, insight, mem_type=MemoryType.REFLECTION, importance=8.5)
    return insight
