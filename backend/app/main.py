"""FastAPI 入口与依赖装配。"""
from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .config import get_settings
from .db import Database
from .emotion import EmotionEngine
from .llm import build_llm_provider
from .memory import MemoryStore, build_embedding_provider
from .orchestrator import Orchestrator
from .schemas import (
    ChatRequest,
    ChatResponse,
    EmotionOut,
    MemoryOut,
    PersonaOut,
    RelationshipOut,
    StateResponse,
)

settings = get_settings()
_db = Database(settings.db_path)
_embedder = build_embedding_provider(settings)
_memory = MemoryStore(_db, _embedder, settings)
_emotion_engine = EmotionEngine()
_llm = build_llm_provider(settings)
_orchestrator = Orchestrator(_db, _memory, _emotion_engine, _llm, settings)

app = FastAPI(title="A-Girl 情感陪伴 NPC", version="0.1.0")

_STATIC_DIR = Path(__file__).resolve().parent.parent / "static"


def _emotion_out(e) -> EmotionOut:
    return EmotionOut(pleasure=e.pleasure, arousal=e.arousal, dominance=e.dominance, label=e.label())


def _relationship_out(r) -> RelationshipOut:
    return RelationshipOut(affinity=r.affinity, stage=r.stage.value)


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "llm": _llm.name, "embedding": settings.embedding_provider}


@app.post("/api/chat", response_model=ChatResponse)
def chat(req: ChatRequest) -> ChatResponse:
    session_id = req.session_id or f"sess-{req.user_id}"
    result = _orchestrator.chat(req.user_id, session_id, req.message)
    return ChatResponse(
        reply=result.reply,
        emotion=_emotion_out(result.emotion),
        relationship=_relationship_out(result.relationship),
        retrieved_memories=result.retrieved_memories,
        is_crisis=result.is_crisis,
        llm=result.llm,
    )


@app.get("/api/state/{user_id}", response_model=StateResponse)
def get_state(user_id: str) -> StateResponse:
    emotion, relationship = _orchestrator.get_state(user_id)
    return StateResponse(
        emotion=_emotion_out(emotion), relationship=_relationship_out(relationship)
    )


@app.get("/api/memory/{user_id}", response_model=list[MemoryOut])
def get_memory(user_id: str) -> list[MemoryOut]:
    mems = _db.all_memories(user_id)
    return [
        MemoryOut(id=m.id, type=m.type.value, content=m.content, importance=m.importance)
        for m in mems
    ]


@app.get("/api/persona", response_model=PersonaOut)
def get_persona() -> PersonaOut:
    p = _orchestrator.persona
    return PersonaOut(
        name=p.name, age=p.age, backstory=p.backstory, speaking_style=p.speaking_style
    )


@app.get("/")
def index() -> FileResponse:
    index_file = _STATIC_DIR / "index.html"
    if not index_file.exists():
        raise HTTPException(status_code=404, detail="frontend not found")
    return FileResponse(index_file)


if _STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=_STATIC_DIR), name="static")
