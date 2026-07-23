from pathlib import Path

from app.config import Settings
from app.db import Database
from app.knowledge.chunker import chunk_markdown
from app.knowledge_scope import KNOWLEDGE_SCOPE_ID
from app.knowledge.goutoujunshi import goutoujunshi_source_paths, ingest_goutoujunshi
from app.memory import MemoryStore, build_embedding_provider


def test_chunk_markdown_splits_by_heading():
    text = "# 标题\n\n第一段。\n\n## 小节\n\n第二段内容。"
    chunks = chunk_markdown(text, max_chars=200)
    assert len(chunks) >= 2
    titles = [t for t, _ in chunks]
    assert any("标题" in t or "小节" in t for t in titles)


def test_ingest_goutoujunshi_from_vendor(tmp_path):
    vendor = tmp_path / "goutoujunshi"
    (vendor / "references" / "knowledge").mkdir(parents=True)
    (vendor / "references" / "practical").mkdir(parents=True)
    (vendor / "references" / "knowledge" / "01-test.md").write_text(
        "# 测试知识\n\n先接住情绪，再谈策略。",
        encoding="utf-8",
    )
    (vendor / "SKILL.md").write_text("# Skill\n\n先接住人，再解决事。", encoding="utf-8")

    db_path = tmp_path / "test.db"
    db = Database(str(db_path))
    settings = Settings(
        db_path=str(db_path),
        knowledge_vendor_path=str(vendor),
        knowledge_reingest=False,
    )
    memory = MemoryStore(db, build_embedding_provider(settings), settings)
    result = ingest_goutoujunshi(memory, db, settings)
    assert result.skipped is False
    assert result.chunks >= 2
    assert db.count_memories(KNOWLEDGE_SCOPE_ID) >= 2


def test_goutoujunshi_source_paths(tmp_path):
    vendor = tmp_path / "repo"
    (vendor / "references" / "knowledge").mkdir(parents=True)
    (vendor / "references" / "knowledge" / "a.md").write_text("# A", encoding="utf-8")
    paths = goutoujunshi_source_paths(vendor)
    assert any(p.name == "a.md" for p in paths)
