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
    AvatarOut,
    ChatRequest,
    ChatResponse,
    EmotionOut,
    MemoryOut,
    PersonaOut,
    ProactiveResponse,
    RelationshipOut,
    StateResponse,
    SttRequest,
    SttResponse,
    TtsOut,
    TtsRequest,
)
from .scheduler import ProactiveScheduler
from .voice import build_stt_provider, build_tts_provider

settings = get_settings()
_db = Database(settings.db_path)
_embedder = build_embedding_provider(settings)
_memory = MemoryStore(_db, _embedder, settings)
_emotion_engine = EmotionEngine()
_llm = build_llm_provider(settings)
_tts = build_tts_provider(settings)
_stt = build_stt_provider(settings)
_orchestrator = Orchestrator(_db, _memory, _emotion_engine, _llm, settings, tts=_tts)

app = FastAPI(title="A-Girl 情感陪伴 NPC", version="0.2.0")

_STATIC_DIR = Path(__file__).resolve().parent.parent / "static"


def _emotion_out(e) -> EmotionOut:
    return EmotionOut(pleasure=e.pleasure, arousal=e.arousal, dominance=e.dominance, label=e.label())


def _relationship_out(r) -> RelationshipOut:
    return RelationshipOut(affinity=r.affinity, stage=r.stage.value)


def _avatar_out(a) -> AvatarOut:
    return AvatarOut(
        expression=a.expression, intensity=a.intensity, animation=a.animation,
        live2d_params=a.live2d_params(),
    )


def _tts_out(t) -> TtsOut | None:
    if t is None:
        return None
    return TtsOut(
        audio_base64=t.audio_base64, format=t.format,
        duration_ms=t.duration_ms, provider=t.provider, lipsync=t.lipsync,
    )


@app.get("/health")
def health() -> dict:
    return {
        "status": "ok", "llm": _llm.name, "embedding": settings.embedding_provider,
        "tts": _tts.name, "stt": _stt.name,
        "audience": settings.audience, "deployment_mode": settings.deployment_mode,
    }


@app.post("/api/chat", response_model=ChatResponse)
def chat(req: ChatRequest) -> ChatResponse:
    session_id = req.session_id or f"sess-{req.user_id}"
    result = _orchestrator.chat(req.user_id, session_id, req.message)
    return ChatResponse(
        reply=result.reply,
        emotion=_emotion_out(result.emotion),
        relationship=_relationship_out(result.relationship),
        avatar=_avatar_out(result.avatar),
        retrieved_memories=result.retrieved_memories,
        is_crisis=result.is_crisis,
        safety_category=result.safety_category,
        llm=result.llm,
        tts=_tts_out(result.tts),
    )


@app.post("/api/tts", response_model=TtsOut)
def tts(req: TtsRequest) -> TtsOut:
    result = _tts.synthesize(req.text, voice=req.voice)
    return _tts_out(result)


@app.post("/api/stt", response_model=SttResponse)
def stt(req: SttRequest) -> SttResponse:
    text = _stt.transcribe(req.audio_base64, fmt=req.format)
    return SttResponse(text=text, provider=_stt.name)


@app.get("/api/proactive/{user_id}", response_model=ProactiveResponse)
def proactive(user_id: str) -> ProactiveResponse:
    """评估是否该主动关心；若是则投递（标记事件已触发、刷新互动时间）。"""
    result, avatar = _orchestrator.deliver_proactive(user_id)
    if not result.should_reach_out:
        return ProactiveResponse(should_reach_out=False)
    tts = _tts.synthesize(result.message) if settings.chat_include_tts and result.message else None
    return ProactiveResponse(
        should_reach_out=True,
        trigger=result.trigger,
        reason=result.reason,
        message=result.message,
        avatar=_avatar_out(avatar) if avatar else None,
        tts=_tts_out(tts),
    )


_scheduler = ProactiveScheduler(_db, _orchestrator, settings)


@app.on_event("startup")
def _on_startup() -> None:
    _scheduler.start()


@app.on_event("shutdown")
def _on_shutdown() -> None:
    _scheduler.stop()


@app.get("/api/proactive/outbox/{user_id}")
def proactive_outbox(user_id: str) -> list[dict]:
    """读取后台调度器投递到内存收件箱的主动消息（嵌入游戏可轮询）。"""
    return _scheduler.drain(user_id)


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
