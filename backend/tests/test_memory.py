import tempfile

import pytest

from app.config import Settings
from app.db import Database
from app.domain import MemoryType
from app.memory import HashEmbeddingProvider, MemoryStore
from app.memory.embeddings import cosine_similarity


@pytest.fixture
def store():
    with tempfile.NamedTemporaryFile(suffix=".db") as f:
        db = Database(f.name)
        s = Settings(db_path=f.name)
        yield MemoryStore(db, HashEmbeddingProvider(dim=256), s)
        db.close()


def test_embedding_similarity_same_text_high():
    emb = HashEmbeddingProvider(dim=256)
    a = emb.embed("我喜欢在夜晚听音乐")
    b = emb.embed("我喜欢在夜晚听音乐")
    assert cosine_similarity(a, b) == pytest.approx(1.0, abs=1e-6)


def test_embedding_similarity_related_higher_than_unrelated():
    emb = HashEmbeddingProvider(dim=256)
    q = emb.embed("我喜欢听音乐")
    related = emb.embed("音乐让我很放松")
    unrelated = emb.embed("明天要去交水电费")
    assert cosine_similarity(q, related) > cosine_similarity(q, unrelated)


def test_retrieve_returns_relevant_memory(store):
    store.add("u1", "ta 喜欢在深夜听爵士乐", importance=5)
    store.add("u1", "ta 养了一只叫橘子的猫", importance=5)
    store.add("u1", "ta 明天要去超市", importance=2)
    results = store.retrieve("u1", "你还记得我喜欢听什么音乐吗", top_k=1)
    assert results
    assert "爵士" in results[0].content


def test_count_excludes_reflections(store):
    store.add("u1", "事件1")
    store.add("u1", "事件2")
    store.add("u1", "高层洞察", mem_type=MemoryType.REFLECTION, importance=8)
    assert store.count("u1") == 2
