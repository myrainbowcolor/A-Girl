"""流式对话延迟优化：重型后处理推迟到 done 之后。"""
import tempfile
from unittest.mock import patch

import pytest

from app.config import Settings
from app.db import Database
from app.emotion import EmotionEngine
from app.llm import MockLLMProvider
from app.memory import HashEmbeddingProvider, MemoryStore
from app.orchestrator import Orchestrator


@pytest.fixture
def orch():
    with tempfile.NamedTemporaryFile(suffix=".db") as f:
        s = Settings(db_path=f.name, chat_defer_heavy_post=True)
        db = Database(f.name)
        mem = MemoryStore(db, HashEmbeddingProvider(dim=256), s)
        o = Orchestrator(db, mem, EmotionEngine(), MockLLMProvider(), s)
        yield o
        db.close()


def test_stream_done_before_heavy_post(orch):
    """流式路径下 done 应先于重型后处理执行。"""
    called = {"before_done": False, "after_done": False}
    seen_done = False

    def side_effect(*args, **kwargs):
        called["before_done"] = not seen_done
        called["after_done"] = seen_done

    with patch.object(orch, "_run_heavy_post_chat", side_effect=side_effect) as mocked:
        for item in orch.chat_stream("u1", "sess-u1", "你好"):
            if item.get("type") == "done":
                seen_done = True
                assert not mocked.called
        assert mocked.called
        assert called["after_done"] is True
        assert called["before_done"] is False
