"""记忆诚实：防止 LLM 编造用户未说过的事。"""
from __future__ import annotations

import re

# 声称「记得用户说过」的常见表述
_MEMORY_CLAIM = re.compile(
    r"(你说过|你之前说过|你告诉过我|你讲过|我记得你|我清楚记得|我真的记得)"
)

# 去掉整句含记忆声称的句子（保留其余）
_CLAIM_SENTENCE = re.compile(
    r"[^。！？!?]*?(?:你说过|你之前说过|你告诉过我|你讲过|我记得你|我清楚记得|我真的记得)"
    r"[^。！？!?]*[。！？!?]?"
)


def _corpus(memories: list, user_texts: list[str]) -> str:
    parts = [m.content for m in memories] + list(user_texts)
    return " ".join(parts)


def enforce_memory_honesty(
    reply: str,
    memories: list,
    user_texts: list[str],
    *,
    fallback: str = "嗯，我在听。你愿意多跟我说说现在的事吗？我不乱猜，以免记错~",
) -> str:
    """若回复声称记得用户说过某事，但语料库中无依据，则去掉幻觉句或回退。

    memories: Memory 对象列表（含 .content）
    user_texts: 本轮会话中用户已发送的消息（含当前轮，调用方传入）
    """
    if not _MEMORY_CLAIM.search(reply):
        return reply

    corpus = _corpus(memories, user_texts)

    # 无记忆且会话极短：大概率是模型瞎编，去掉声称句
    if not memories and len(user_texts) <= 2:
        cleaned = _CLAIM_SENTENCE.sub("", reply).strip()
        cleaned = re.sub(r"\s+", "", cleaned)
        if len(cleaned) < 4:
            return fallback
        return cleaned

    # 有记忆但仍可能张冠李戴（如把 NPC 兴趣说成用户的）：去掉无法在原句找到依据的声称
    # 简化策略：若声称句中的关键词（音乐/散步等）不在语料库，删该句
    sentences = re.split(r"(?<=[。！？!?])", reply)
    kept: list[str] = []
    for sent in sentences:
        if not sent.strip():
            continue
        if _MEMORY_CLAIM.search(sent):
            keywords = re.findall(r"[\u4e00-\u9fff]{2,}", sent)
            expanded: list[str] = []
            for k in keywords:
                if len(k) <= 6:
                    expanded.append(k)
                else:
                    expanded.extend(k[i : i + 2] for i in range(len(k) - 1))
            expanded = [k for k in expanded if k not in _STOPWORDS]
            if expanded and not any(k in corpus for k in expanded):
                continue
        kept.append(sent)
    result = "".join(kept).strip()
    return result if len(result) >= 2 else fallback


_STOPWORDS = {
    "你说过", "我记得", "之前", "告诉", "清楚", "真的", "我们", "可以",
    "什么", "怎么", "是不是", "有没有", "一下", "今天", "最近", "愿意",
}
