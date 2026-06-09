"""API 请求/响应模型。"""
from __future__ import annotations

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    user_id: str = Field(..., description="用户唯一标识")
    message: str = Field(..., min_length=1, description="用户输入")
    session_id: str | None = Field(None, description="会话 ID，缺省按 user_id 派生")


class EmotionOut(BaseModel):
    pleasure: float
    arousal: float
    dominance: float
    label: str


class RelationshipOut(BaseModel):
    affinity: float
    stage: str


class AvatarOut(BaseModel):
    expression: str
    intensity: float
    animation: str
    live2d_params: dict[str, float] = {}


class TtsOut(BaseModel):
    audio_base64: str
    format: str
    duration_ms: int
    provider: str
    lipsync: list[dict] = []
    visemes: list[dict] = []
    style: dict | None = None


class ChatResponse(BaseModel):
    reply: str
    emotion: EmotionOut
    relationship: RelationshipOut
    avatar: AvatarOut
    retrieved_memories: list[str]
    is_crisis: bool
    safety_category: str | None = None
    llm: str
    tts: TtsOut | None = None


class TtsRequest(BaseModel):
    text: str = Field(..., min_length=1)
    voice: str | None = None
    # 可选：直接给情绪让语音带风格（缺省 neutral）
    pleasure: float | None = None
    arousal: float | None = None


class SttRequest(BaseModel):
    audio_base64: str = Field(..., description="base64 编码的音频")
    format: str = Field("wav", description="音频格式")


class SttResponse(BaseModel):
    text: str
    provider: str


class ConsentRequest(BaseModel):
    user_id: str
    age: int = Field(..., ge=0, le=120)


class ConsentResponse(BaseModel):
    ok: bool
    reason: str | None = None


class ProactiveResponse(BaseModel):
    should_reach_out: bool
    trigger: str | None = None
    reason: str | None = None
    message: str | None = None
    avatar: AvatarOut | None = None
    tts: TtsOut | None = None


class StateResponse(BaseModel):
    emotion: EmotionOut
    relationship: RelationshipOut


class PersonaOut(BaseModel):
    name: str
    age: int
    backstory: str
    speaking_style: str


class MemoryOut(BaseModel):
    id: int | None
    type: str
    content: str
    importance: float
