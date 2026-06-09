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


class ChatResponse(BaseModel):
    reply: str
    emotion: EmotionOut
    relationship: RelationshipOut
    retrieved_memories: list[str]
    is_crisis: bool
    llm: str


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
