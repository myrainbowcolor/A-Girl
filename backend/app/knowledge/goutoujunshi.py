"""狗头军师（goutoujunshi）知识库入库。"""
from __future__ import annotations

import subprocess
from pathlib import Path

from ..config import Settings
from ..db import Database
from ..memory.store import MemoryStore
from ..knowledge_scope import GOUTOUJUNSHI_SOURCE
from .loader import IngestResult, collect_markdown_files, ingest_markdown_sources

REPO_URL = "https://github.com/powerycy/goutoujunshi.git"


def default_vendor_path() -> Path:
    return Path(__file__).resolve().parents[3] / "knowledge" / "vendor" / "goutoujunshi"


def ensure_goutoujunshi_repo(vendor_path: Path, repo_url: str = REPO_URL) -> Path:
    """克隆或更新狗头军师仓库到本地 vendor 目录。"""
    vendor_path = vendor_path.expanduser().resolve()
    vendor_path.parent.mkdir(parents=True, exist_ok=True)

    if (vendor_path / ".git").is_dir():
        subprocess.run(
            ["git", "-C", str(vendor_path), "pull", "--ff-only"],
            check=False,
            capture_output=True,
            text=True,
        )
        return vendor_path

    if vendor_path.exists() and any(vendor_path.rglob("*.md")):
        return vendor_path

    if vendor_path.exists() and any(vendor_path.iterdir()):
        raise FileExistsError(f"目标目录已存在且不是 git 仓库: {vendor_path}")

    subprocess.run(
        ["git", "clone", "--depth", "1", repo_url, str(vendor_path)],
        check=True,
    )
    return vendor_path


def goutoujunshi_source_paths(vendor_path: Path) -> list[Path]:
    root = vendor_path.resolve()
    return collect_markdown_files(
        root / "references" / "knowledge",
        root / "references" / "practical",
        root / "SKILL.md",
    )


def ingest_goutoujunshi(
    memory: MemoryStore,
    db: Database,
    settings: Settings,
) -> IngestResult:
    vendor = Path(settings.knowledge_vendor_path).expanduser() if settings.knowledge_vendor_path else default_vendor_path()
    ensure_goutoujunshi_repo(vendor, settings.knowledge_repo_url or REPO_URL)
    sources = goutoujunshi_source_paths(vendor)
    if not sources:
        return IngestResult(
            source=GOUTOUJUNSHI_SOURCE,
            files=0,
            chunks=0,
            message=f"未在 {vendor} 找到 Markdown 知识文件",
        )

    # 相对路径用于 chunk 标签
    normalized: list[Path] = []
    for path in sources:
        try:
            rel = path.relative_to(vendor)
            normalized.append(rel)
        except ValueError:
            normalized.append(path)

    # ingest 需要可读绝对路径
    files_to_ingest = [vendor / p if not p.is_absolute() else p for p in normalized]
    # 重写 loader 使用相对路径标签
    return _ingest_with_relative_labels(
        memory,
        db,
        vendor,
        files_to_ingest,
        reingest=settings.knowledge_reingest,
    )


def _ingest_with_relative_labels(
    memory: MemoryStore,
    db: Database,
    vendor: Path,
    files: list[Path],
    *,
    reingest: bool,
) -> IngestResult:
    from ..domain import MemoryType
    from .chunker import chunk_markdown
    from ..knowledge_scope import KNOWLEDGE_SCOPE_ID
    from .loader import IngestResult as IR

    scope_id = KNOWLEDGE_SCOPE_ID
    if not reingest and db.count_memories(scope_id) > 0:
        count = db.count_memories(scope_id)
        return IR(
            source=GOUTOUJUNSHI_SOURCE,
            files=0,
            chunks=0,
            skipped=True,
            message=f"已存在 {count} 条知识记忆，跳过（AGIRL_KNOWLEDGE_REINGEST=true 可重建）",
        )
    if reingest:
        db.delete_memories(scope_id)

    files_n = 0
    chunks_n = 0
    for path in files:
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        rel = str(path.relative_to(vendor)).replace("\\", "/")
        for section, body in chunk_markdown(text):
            content = f"[知识:{GOUTOUJUNSHI_SOURCE}/{rel}#{section}]\n{body.strip()}"
            memory.add(scope_id, content, mem_type=MemoryType.SEMANTIC, importance=8.0)
            chunks_n += 1
        files_n += 1

    return IR(
        source=GOUTOUJUNSHI_SOURCE,
        files=files_n,
        chunks=chunks_n,
        message=f"狗头军师知识已入库：{files_n} 文件 / {chunks_n} 片段",
    )
