"""SQLite 持久化层（开发期）。

封装连接与建表；生产期可替换为 PostgreSQL + pgvector，仓储接口保持不变。
"""
from __future__ import annotations

import json
import sqlite3
import threading
from typing import Optional

from .domain import EmotionState, Memory, MemoryType, Message, Relationship, RelationshipStage

_SCHEMA = """
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    role TEXT NOT NULL,
    content TEXT NOT NULL,
    sentiment REAL DEFAULT 0,
    created_at REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS memories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    type TEXT NOT NULL,
    content TEXT NOT NULL,
    importance REAL DEFAULT 3,
    embedding TEXT NOT NULL,
    created_at REAL NOT NULL,
    last_access REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS emotion_state (
    user_id TEXT PRIMARY KEY,
    pleasure REAL, arousal REAL, dominance REAL, updated_at REAL
);
CREATE TABLE IF NOT EXISTS relationship (
    user_id TEXT PRIMARY KEY,
    affinity REAL, stage TEXT, updated_at REAL
);
CREATE INDEX IF NOT EXISTS idx_messages_session ON messages(session_id);
CREATE INDEX IF NOT EXISTS idx_memories_user ON memories(user_id);
"""


class Database:
    def __init__(self, path: str) -> None:
        self._path = path
        self._lock = threading.Lock()
        self._conn = sqlite3.connect(path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._conn.executescript(_SCHEMA)
        self._conn.commit()

    def close(self) -> None:
        self._conn.close()

    # ---------- messages ----------
    def add_message(self, msg: Message) -> Message:
        with self._lock:
            cur = self._conn.execute(
                "INSERT INTO messages(session_id, role, content, sentiment, created_at)"
                " VALUES(?,?,?,?,?)",
                (msg.session_id, msg.role, msg.content, msg.sentiment, msg.created_at),
            )
            self._conn.commit()
            msg.id = cur.lastrowid
        return msg

    def recent_messages(self, session_id: str, limit: int) -> list[Message]:
        cur = self._conn.execute(
            "SELECT * FROM messages WHERE session_id=? ORDER BY id DESC LIMIT ?",
            (session_id, limit),
        )
        rows = cur.fetchall()[::-1]
        return [
            Message(
                id=r["id"], session_id=r["session_id"], role=r["role"],
                content=r["content"], sentiment=r["sentiment"], created_at=r["created_at"],
            )
            for r in rows
        ]

    # ---------- memories ----------
    def add_memory(self, mem: Memory) -> Memory:
        with self._lock:
            cur = self._conn.execute(
                "INSERT INTO memories(user_id, type, content, importance, embedding, created_at, last_access)"
                " VALUES(?,?,?,?,?,?,?)",
                (
                    mem.user_id, mem.type.value, mem.content, mem.importance,
                    json.dumps(mem.embedding), mem.created_at, mem.last_access,
                ),
            )
            self._conn.commit()
            mem.id = cur.lastrowid
        return mem

    def all_memories(self, user_id: str) -> list[Memory]:
        cur = self._conn.execute("SELECT * FROM memories WHERE user_id=?", (user_id,))
        return [self._row_to_memory(r) for r in cur.fetchall()]

    def count_memories(self, user_id: str) -> int:
        cur = self._conn.execute(
            "SELECT COUNT(*) AS c FROM memories WHERE user_id=? AND type!=?",
            (user_id, MemoryType.REFLECTION.value),
        )
        return cur.fetchone()["c"]

    def touch_memory(self, memory_id: int, last_access: float) -> None:
        with self._lock:
            self._conn.execute(
                "UPDATE memories SET last_access=? WHERE id=?", (last_access, memory_id)
            )
            self._conn.commit()

    @staticmethod
    def _row_to_memory(r: sqlite3.Row) -> Memory:
        return Memory(
            id=r["id"], user_id=r["user_id"], type=MemoryType(r["type"]),
            content=r["content"], importance=r["importance"],
            embedding=json.loads(r["embedding"]), created_at=r["created_at"],
            last_access=r["last_access"],
        )

    # ---------- emotion ----------
    def get_emotion(self, user_id: str) -> Optional[EmotionState]:
        cur = self._conn.execute("SELECT * FROM emotion_state WHERE user_id=?", (user_id,))
        r = cur.fetchone()
        if not r:
            return None
        return EmotionState(pleasure=r["pleasure"], arousal=r["arousal"], dominance=r["dominance"])

    def save_emotion(self, user_id: str, e: EmotionState, updated_at: float) -> None:
        with self._lock:
            self._conn.execute(
                "INSERT INTO emotion_state(user_id, pleasure, arousal, dominance, updated_at)"
                " VALUES(?,?,?,?,?) ON CONFLICT(user_id) DO UPDATE SET"
                " pleasure=excluded.pleasure, arousal=excluded.arousal,"
                " dominance=excluded.dominance, updated_at=excluded.updated_at",
                (user_id, e.pleasure, e.arousal, e.dominance, updated_at),
            )
            self._conn.commit()

    # ---------- relationship ----------
    def get_relationship(self, user_id: str) -> Optional[Relationship]:
        cur = self._conn.execute("SELECT * FROM relationship WHERE user_id=?", (user_id,))
        r = cur.fetchone()
        if not r:
            return None
        return Relationship(affinity=r["affinity"], stage=RelationshipStage(r["stage"]))

    def save_relationship(self, user_id: str, rel: Relationship, updated_at: float) -> None:
        with self._lock:
            self._conn.execute(
                "INSERT INTO relationship(user_id, affinity, stage, updated_at)"
                " VALUES(?,?,?,?) ON CONFLICT(user_id) DO UPDATE SET"
                " affinity=excluded.affinity, stage=excluded.stage, updated_at=excluded.updated_at",
                (user_id, rel.affinity, rel.stage.value, updated_at),
            )
            self._conn.commit()
