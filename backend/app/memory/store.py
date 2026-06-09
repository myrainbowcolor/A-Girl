"""记忆流与检索。

实现 Generative Agents 风格的检索打分：相关性 + 时近性 + 重要性。
"""
from __future__ import annotations

import math
import time

from ..config import Settings
from ..db import Database
from ..domain import Memory, MemoryType
from .embeddings import EmbeddingProvider, cosine_similarity

# 时近性指数衰减半衰期（秒）：约 3 天
_RECENCY_HALFLIFE = 3 * 24 * 3600


class MemoryStore:
    def __init__(self, db: Database, embedder: EmbeddingProvider, settings: Settings) -> None:
        self._db = db
        self._embedder = embedder
        self._s = settings

    def add(
        self,
        user_id: str,
        content: str,
        mem_type: MemoryType = MemoryType.EPISODIC,
        importance: float = 3.0,
    ) -> Memory:
        now = time.time()
        mem = Memory(
            user_id=user_id,
            content=content,
            type=mem_type,
            importance=max(1.0, min(10.0, importance)),
            embedding=self._embedder.embed(content),
            created_at=now,
            last_access=now,
        )
        return self._db.add_memory(mem)

    def retrieve(self, user_id: str, query: str, top_k: int | None = None) -> list[Memory]:
        top_k = top_k or self._s.memory_top_k
        memories = self._db.all_memories(user_id)
        if not memories:
            return []

        query_vec = self._embedder.embed(query)
        now = time.time()
        scored: list[tuple[float, Memory]] = []
        for m in memories:
            relevance = cosine_similarity(query_vec, m.embedding)
            recency = math.exp(-(now - m.last_access) / _RECENCY_HALFLIFE)
            importance = m.importance / 10.0
            score = (
                self._s.memory_weight_relevance * relevance
                + self._s.memory_weight_recency * recency
                + self._s.memory_weight_importance * importance
            )
            scored.append((score, m))

        scored.sort(key=lambda x: x[0], reverse=True)
        top = [m for _, m in scored[:top_k]]
        for m in top:
            if m.id is not None:
                self._db.touch_memory(m.id, now)
        return top

    def count(self, user_id: str) -> int:
        return self._db.count_memories(user_id)
