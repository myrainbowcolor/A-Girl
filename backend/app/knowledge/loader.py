"""将 Markdown 知识文件写入记忆流。"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from ..db import Database
from ..domain import MemoryType
from ..memory.store import MemoryStore
from .chunker import chunk_markdown
from ..knowledge_scope import KNOWLEDGE_SCOPE_ID


@dataclass(frozen=True)
class IngestResult:
    source: str
    files: int
    chunks: int
    skipped: bool = False
    message: str = ""


def _format_chunk(source: str, rel_path: str, section: str, body: str) -> str:
    section = section.replace("\n", " ").strip()
    return f"[知识:{source}/{rel_path}#{section}]\n{body.strip()}"


def ingest_markdown_sources(
    memory: MemoryStore,
    db: Database,
    sources: list[Path],
    *,
    source: str,
    scope_id: str = KNOWLEDGE_SCOPE_ID,
    reingest: bool = False,
    importance: float = 7.5,
) -> IngestResult:
    """批量入库 Markdown；默认跳过已入库内容。"""
    if not reingest and db.count_memories(scope_id) > 0:
        count = db.count_memories(scope_id)
        return IngestResult(
            source=source,
            files=0,
            chunks=0,
            skipped=True,
            message=f"已存在 {count} 条知识记忆，跳过（设置 reingest=true 可重建）",
        )

    if reingest:
        db.delete_memories(scope_id)

    files = 0
    chunks = 0
    for path in sources:
        if not path.is_file() or path.suffix.lower() not in {".md", ".markdown"}:
            continue
        text = path.read_text(encoding="utf-8")
        rel = path.name if len(sources) == 1 and path.name.endswith(".md") else str(path)
        for section, body in chunk_markdown(text):
            content = _format_chunk(source, rel, section, body)
            memory.add(
                scope_id,
                content,
                mem_type=MemoryType.SEMANTIC,
                importance=importance,
            )
            chunks += 1
        files += 1

    return IngestResult(
        source=source,
        files=files,
        chunks=chunks,
        message=f"已入库 {files} 个文件、{chunks} 个片段",
    )


def collect_markdown_files(*roots: Path) -> list[Path]:
    out: list[Path] = []
    for root in roots:
        if root.is_file() and root.suffix.lower() == ".md":
            out.append(root)
            continue
        if not root.is_dir():
            continue
        out.extend(sorted(root.rglob("*.md")))
    # 去重并保持稳定顺序
    seen: set[Path] = set()
    unique: list[Path] = []
    for path in out:
        key = path.resolve()
        if key in seen:
            continue
        seen.add(key)
        unique.append(path)
    return unique
