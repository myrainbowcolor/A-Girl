"""SQLite 持久化层（开发期）。

封装连接与建表；生产期可替换为 PostgreSQL + pgvector，仓储接口保持不变。
"""
from __future__ import annotations

import json
import sqlite3
import threading
from typing import Optional

from .domain import (
    EmotionState,
    Event,
    Memory,
    MemoryType,
    Message,
    Relationship,
    RelationshipStage,
    UserMeta,
)

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
CREATE TABLE IF NOT EXISTS user_meta (
    user_id TEXT PRIMARY KEY,
    last_interaction_at REAL DEFAULT 0,
    last_sentiment REAL DEFAULT 0,
    sentiment_ema REAL DEFAULT 0,
    interaction_count INTEGER DEFAULT 0,
    relationship_summary TEXT DEFAULT '',
    relationship_health REAL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    kind TEXT NOT NULL,
    label TEXT NOT NULL,
    trigger_at REAL NOT NULL,
    created_at REAL NOT NULL,
    fired INTEGER DEFAULT 0
);
CREATE TABLE IF NOT EXISTS user_consent (
    user_id TEXT PRIMARY KEY,
    age INTEGER,
    consented_at REAL
);
CREATE TABLE IF NOT EXISTS audit_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    category TEXT NOT NULL,
    excerpt TEXT,
    created_at REAL NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_messages_session ON messages(session_id);
CREATE INDEX IF NOT EXISTS idx_memories_user ON memories(user_id);
CREATE INDEX IF NOT EXISTS idx_events_user ON events(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_user ON audit_events(user_id);
"""


class Database:
    def __init__(self, path: str) -> None:
        self._path = path
        self._lock = threading.Lock()
        self._conn = sqlite3.connect(path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._conn.executescript(_SCHEMA)
        self._conn.commit()
        self._migrate()

    def _migrate(self) -> None:
        """增量迁移：为旧库补列。"""
        cols = {r[1] for r in self._conn.execute("PRAGMA table_info(user_meta)")}
        for name, typedef in (
            ("sentiment_ema", "REAL DEFAULT 0"),
            ("interaction_count", "INTEGER DEFAULT 0"),
            ("relationship_summary", "TEXT DEFAULT ''"),
            ("relationship_health", "REAL DEFAULT 0"),
        ):
            if name not in cols:
                self._conn.execute(f"ALTER TABLE user_meta ADD COLUMN {name} {typedef}")
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

    def has_chat_history(self, user_id: str) -> bool:
        cur = self._conn.execute(
            "SELECT 1 FROM messages WHERE session_id=? LIMIT 1",
            (f"sess-{user_id}",),
        )
        return cur.fetchone() is not None

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

    # ---------- user_meta ----------
    def get_user_meta(self, user_id: str) -> Optional[UserMeta]:
        cur = self._conn.execute("SELECT * FROM user_meta WHERE user_id=?", (user_id,))
        r = cur.fetchone()
        if not r:
            return None
        return UserMeta(
            user_id=r["user_id"],
            last_interaction_at=r["last_interaction_at"],
            last_sentiment=r["last_sentiment"],
            sentiment_ema=r["sentiment_ema"] if "sentiment_ema" in r.keys() else 0.0,
            interaction_count=r["interaction_count"] if "interaction_count" in r.keys() else 0,
            relationship_summary=r["relationship_summary"] if "relationship_summary" in r.keys() else "",
            relationship_health=r["relationship_health"] if "relationship_health" in r.keys() else 0.0,
        )

    def save_user_meta(self, meta: UserMeta) -> None:
        with self._lock:
            self._conn.execute(
                "INSERT INTO user_meta("
                "user_id, last_interaction_at, last_sentiment, sentiment_ema,"
                " interaction_count, relationship_summary, relationship_health"
                ") VALUES(?,?,?,?,?,?,?) ON CONFLICT(user_id) DO UPDATE SET"
                " last_interaction_at=excluded.last_interaction_at,"
                " last_sentiment=excluded.last_sentiment,"
                " sentiment_ema=excluded.sentiment_ema,"
                " interaction_count=excluded.interaction_count,"
                " relationship_summary=excluded.relationship_summary,"
                " relationship_health=excluded.relationship_health",
                (
                    meta.user_id,
                    meta.last_interaction_at,
                    meta.last_sentiment,
                    meta.sentiment_ema,
                    meta.interaction_count,
                    meta.relationship_summary,
                    meta.relationship_health,
                ),
            )
            self._conn.commit()

    def all_user_ids(self) -> list[str]:
        cur = self._conn.execute("SELECT user_id FROM user_meta")
        return [r["user_id"] for r in cur.fetchall()]

    # ---------- events ----------
    def add_event(self, ev: Event) -> Event:
        with self._lock:
            cur = self._conn.execute(
                "INSERT INTO events(user_id, kind, label, trigger_at, created_at, fired)"
                " VALUES(?,?,?,?,?,?)",
                (ev.user_id, ev.kind, ev.label, ev.trigger_at, ev.created_at, int(ev.fired)),
            )
            self._conn.commit()
            ev.id = cur.lastrowid
        return ev

    def pending_events(self, user_id: str) -> list[Event]:
        cur = self._conn.execute(
            "SELECT * FROM events WHERE user_id=? AND fired=0 ORDER BY trigger_at", (user_id,)
        )
        return [
            Event(
                id=r["id"], user_id=r["user_id"], kind=r["kind"], label=r["label"],
                trigger_at=r["trigger_at"], created_at=r["created_at"], fired=bool(r["fired"]),
            )
            for r in cur.fetchall()
        ]

    def mark_event_fired(self, event_id: int) -> None:
        with self._lock:
            self._conn.execute("UPDATE events SET fired=1 WHERE id=?", (event_id,))
            self._conn.commit()

    # ---------- consent (age gate) ----------
    def get_consent(self, user_id: str) -> Optional[dict]:
        cur = self._conn.execute("SELECT * FROM user_consent WHERE user_id=?", (user_id,))
        r = cur.fetchone()
        if not r:
            return None
        return {"user_id": r["user_id"], "age": r["age"], "consented_at": r["consented_at"]}

    def save_consent(self, user_id: str, age: int, consented_at: float) -> None:
        with self._lock:
            self._conn.execute(
                "INSERT INTO user_consent(user_id, age, consented_at) VALUES(?,?,?)"
                " ON CONFLICT(user_id) DO UPDATE SET age=excluded.age,"
                " consented_at=excluded.consented_at",
                (user_id, age, consented_at),
            )
            self._conn.commit()

    # ---------- audit ----------
    def add_audit_event(self, user_id: str, category: str, excerpt: str, created_at: float) -> None:
        with self._lock:
            self._conn.execute(
                "INSERT INTO audit_events(user_id, category, excerpt, created_at) VALUES(?,?,?,?)",
                (user_id, category, excerpt, created_at),
            )
            self._conn.commit()

    def audit_events(self, user_id: str, limit: int = 100) -> list[dict]:
        cur = self._conn.execute(
            "SELECT * FROM audit_events WHERE user_id=? ORDER BY id DESC LIMIT ?",
            (user_id, limit),
        )
        return [
            {"id": r["id"], "category": r["category"], "excerpt": r["excerpt"],
             "created_at": r["created_at"]}
            for r in cur.fetchall()
        ]
