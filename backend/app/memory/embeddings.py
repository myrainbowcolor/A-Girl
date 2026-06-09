"""Embedding 抽象。

骨架阶段提供确定性哈希向量降级实现：无需任何外部 Key，即可让向量检索
逻辑端到端跑通并可测试。生产期可替换为真实 embedding 服务。
"""
from __future__ import annotations

import hashlib
import math
import re
from abc import ABC, abstractmethod

from ..config import Settings


class EmbeddingProvider(ABC):
    @abstractmethod
    def embed(self, text: str) -> list[float]:
        raise NotImplementedError


_TOKEN_RE = re.compile(r"[\w\u4e00-\u9fff]+")


class HashEmbeddingProvider(EmbeddingProvider):
    """基于词哈希的稀疏-稠密降级向量（bag-of-tokens 投影到固定维度）。

    对中文按字/词混合切分，保证"相同/相似文本"得到相近向量，
    足以驱动并验证检索打分逻辑。
    """

    def __init__(self, dim: int = 256) -> None:
        self._dim = dim

    def _tokens(self, text: str) -> list[str]:
        text = text.lower()
        tokens: list[str] = []
        for chunk in _TOKEN_RE.findall(text):
            if re.search(r"[\u4e00-\u9fff]", chunk):
                # 中文：按单字 + 相邻二元组
                tokens.extend(list(chunk))
                tokens.extend(chunk[i : i + 2] for i in range(len(chunk) - 1))
            else:
                tokens.append(chunk)
        return tokens

    def embed(self, text: str) -> list[float]:
        vec = [0.0] * self._dim
        for tok in self._tokens(text):
            h = int(hashlib.md5(tok.encode("utf-8")).hexdigest(), 16)
            idx = h % self._dim
            sign = 1.0 if (h >> 8) % 2 == 0 else -1.0
            vec[idx] += sign
        norm = math.sqrt(sum(v * v for v in vec))
        if norm > 0:
            vec = [v / norm for v in vec]
        return vec


def cosine_similarity(a: list[float], b: list[float]) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


def build_embedding_provider(settings: Settings) -> EmbeddingProvider:
    # 预留 openai_compatible embedding；当前默认哈希降级，保证离线可用
    return HashEmbeddingProvider(dim=settings.embedding_dim)
