"""FastAPI 入口与依赖装配。"""
from __future__ import annotations

import json
import queue
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles

from .compliance import AgeGate, AuditLogger
from .config import get_settings
from .db import Database
from .emotion import EmotionEngine
from .llm import build_llm_provider
from .memory import MemoryStore, build_embedding_provider
from .orchestrator import Orchestrator
from .push import PushHub
from .schemas import (
    AvatarOut,
    ChatRequest,
    ChatResponse,
    ConsentRequest,
    ConsentResponse,
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
_audit = AuditLogger(_db, settings.audit_log_path)
_age_gate = AgeGate(_db, require=settings.require_age_gate, min_age=settings.min_age)
_push = PushHub(settings)
_orchestrator = Orchestrator(
    _db, _memory, _emotion_engine, _llm, settings, tts=_tts, audit=_audit
)

app = FastAPI(title="A-Girl 情感陪伴 NPC", version="0.3.0")

_STATIC_DIR = Path(__file__).resolve().parent.parent / "static"


def _emotion_out(e) -> EmotionOut:
    return EmotionOut(pleasure=e.pleasure, arousal=e.arousal, dominance=e.dominance, label=e.label())


def _relationship_out(r, summary: str = "", health: float = 0.0, trend: str = "new") -> RelationshipOut:
    return RelationshipOut(
        affinity=r.affinity,
        stage=r.stage.value,
        health_score=health,
        summary=summary,
        trend=trend,
    )


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
        visemes=t.visemes, style=t.style,
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
    # 未成年人合规：未完成年龄确认前不允许对话
    if not _age_gate.has_consent(req.user_id):
        raise HTTPException(status_code=403, detail="age_gate_required")
    session_id = req.session_id or f"sess-{req.user_id}"
    result = _orchestrator.chat(req.user_id, session_id, req.message)
    return ChatResponse(
        reply=result.reply,
        emotion=_emotion_out(result.emotion),
        relationship=_relationship_out(
            result.relationship,
            summary=result.relationship_summary,
            health=result.relationship_health,
            trend=result.relationship_trend,
        ),
        avatar=_avatar_out(result.avatar),
        retrieved_memories=result.retrieved_memories,
        is_crisis=result.is_crisis,
        safety_category=result.safety_category,
        llm=result.llm,
        tts=_tts_out(result.tts),
        user_sentiment_label=result.user_sentiment_label,
    )


@app.post("/api/chat/stream")
def chat_stream(req: ChatRequest) -> StreamingResponse:
    """SSE 流式对话：event 顺序 meta → token* → done。"""
    if not _age_gate.has_consent(req.user_id):
        raise HTTPException(status_code=403, detail="age_gate_required")
    session_id = req.session_id or f"sess-{req.user_id}"

    def event_gen():
        try:
            for item in _orchestrator.chat_stream(req.user_id, session_id, req.message):
                yield f"data: {json.dumps(item, ensure_ascii=False)}\n\n"
        except Exception as exc:
            err = {"type": "error", "message": str(exc)}
            yield f"data: {json.dumps(err, ensure_ascii=False)}\n\n"

    return StreamingResponse(
        event_gen(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@app.post("/api/tts", response_model=TtsOut)
def tts(req: TtsRequest) -> TtsOut:
    style = None
    if req.pleasure is not None or req.arousal is not None:
        from .domain import EmotionState
        from .voice import style_from_emotion
        style = style_from_emotion(
            EmotionState(pleasure=req.pleasure or 0.0, arousal=req.arousal or 0.0),
            user_sentiment=req.user_sentiment,
        )
    result = _tts.synthesize(req.text, voice=req.voice, style=style)
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
    emotion, relationship = _orchestrator.get_state(user_id)
    tts = _tts.synthesize(result.message) if settings.chat_include_tts and result.message else None
    return ProactiveResponse(
        should_reach_out=True,
        trigger=result.trigger,
        reason=result.reason,
        message=result.message,
        avatar=_avatar_out(avatar) if avatar else None,
        emotion=_emotion_out(emotion),
        relationship=_relationship_out(relationship),
        tts=_tts_out(tts),
    )


@app.post("/api/consent", response_model=ConsentResponse)
def consent(req: ConsentRequest) -> ConsentResponse:
    """年龄确认门：记录用户年龄确认，通过后才能对话。"""
    result = _age_gate.record_consent(req.user_id, req.age)
    return ConsentResponse(ok=result["ok"], reason=result["reason"])


@app.get("/api/consent/{user_id}")
def consent_status(user_id: str) -> dict:
    return {"has_consent": _age_gate.has_consent(user_id), "required": _age_gate.required}


@app.get("/api/audit/{user_id}")
def audit(user_id: str, limit: int = 100) -> list[dict]:
    """家长可见安全审计日志（危机/成人/暴力/隐私等事件）。"""
    return _db.audit_events(user_id, limit=limit)


@app.get("/api/stream/{user_id}")
def stream(user_id: str) -> StreamingResponse:
    """SSE 主动推送：客户端订阅后实时收到主动关心消息。"""
    q = _push.subscribe(user_id)

    def event_gen():
        try:
            # 首帧握手，便于客户端确认连接
            yield "event: ready\ndata: {}\n\n"
            while True:
                try:
                    item = q.get(timeout=15)
                    yield f"data: {json.dumps(item, ensure_ascii=False)}\n\n"
                except queue.Empty:
                    yield ": keep-alive\n\n"  # 心跳
        finally:
            _push.unsubscribe(user_id, q)

    return StreamingResponse(event_gen(), media_type="text/event-stream")


@app.post("/api/proactive/{user_id}/push")
def proactive_push(user_id: str) -> dict:
    """评估主动关心并通过 SSE/webhook 推送（用于手动触发与测试）。"""
    result, avatar = _orchestrator.deliver_proactive(user_id)
    if not result.should_reach_out:
        return {"should_reach_out": False}
    item = {
        "type": "proactive", "trigger": result.trigger, "reason": result.reason,
        "message": result.message,
        "avatar": {"expression": avatar.expression, "intensity": avatar.intensity,
                   "animation": avatar.animation} if avatar else None,
    }
    stats = _push.publish(user_id, item)
    return {"should_reach_out": True, **item, "delivery": stats}


_scheduler = ProactiveScheduler(_db, _orchestrator, settings, push=_push)


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
    meta = _db.get_user_meta(user_id)
    return StateResponse(
        emotion=_emotion_out(emotion),
        relationship=_relationship_out(
            relationship,
            summary=meta.relationship_summary if meta else "",
            health=meta.relationship_health if meta else 0.0,
            trend="stable",
        ),
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
