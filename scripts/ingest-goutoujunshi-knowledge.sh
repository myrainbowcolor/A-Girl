#!/usr/bin/env bash
# 将狗头军师（goutoujunshi）知识库入库到 A-Girl 记忆流
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT/backend"
python3 - <<'PY'
from app.config import get_settings
from app.db import Database
from app.knowledge.goutoujunshi import ingest_goutoujunshi
from app.knowledge_scope import KNOWLEDGE_SCOPE_ID
from app.memory import MemoryStore, build_embedding_provider

settings = get_settings()
db = Database(settings.db_path)
memory = MemoryStore(db, build_embedding_provider(settings), settings)
result = ingest_goutoujunshi(memory, db, settings)
total = db.count_memories(KNOWLEDGE_SCOPE_ID)
print(f"[knowledge] {result.message}")
print(f"[knowledge] total={total} skipped={result.skipped}")
PY
