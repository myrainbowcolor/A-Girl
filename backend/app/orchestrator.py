"""对话编排：串联感知 → 安全 → 记忆检索 → 情绪评估 → 生成 → 状态更新。"""
from __future__ import annotations

import time
from collections.abc import Iterator
from dataclasses import dataclass
from typing import Any

from .avatar import AvatarCue, emotion_to_avatar
from .config import Settings
from .db import Database
from .domain import EmotionState, MemoryType, Message, Persona, Relationship, UserMeta
from .emotion import EmotionEngine
from .emotion.relationship_insight import RelationshipInsight, build_insight
from .llm import LLMProvider
from .memory import MemoryStore
from .memory.reflection import maybe_reflect
from .memory_honesty import enforce_memory_honesty
from .persona import build_system_prompt, default_persona
from .compliance import AuditLogger
from .proactivity import ProactiveResult, ProactivityEngine, extract_events
from .safety import SafetyCategory, check_safety, minor_guard_prompt
from .voice import TTSProvider, style_from_emotion
from .voice.base import TTSResult


@dataclass
class ChatResult:
    reply: str
    emotion: EmotionState
    relationship: Relationship
    avatar: AvatarCue
    retrieved_memories: list[str]
    is_crisis: bool
    llm: str
    safety_category: str | None = None
    tts: TTSResult | None = None
    relationship_summary: str = ""
    relationship_health: float = 0.0
    relationship_trend: str = "new"
    user_sentiment_label: str = ""


class Orchestrator:
    def __init__(
        self,
        db: Database,
        memory: MemoryStore,
        emotion_engine: EmotionEngine,
        llm: LLMProvider,
        settings: Settings,
        persona: Persona | None = None,
        tts: TTSProvider | None = None,
        audit: "AuditLogger | None" = None,
    ) -> None:
        self._db = db
        self._memory = memory
        self._emotion_engine = emotion_engine
        self._llm = llm
        self._s = settings
        self._persona = persona or default_persona()
        self._tts = tts
        self._audit = audit
        self._proactivity = ProactivityEngine(db, settings, self._persona)

    @property
    def persona(self) -> Persona:
        return self._persona

    def _record_interaction(self, user_id: str, now: float, sentiment: float) -> UserMeta:
        meta = self._db.get_user_meta(user_id) or UserMeta(user_id=user_id)
        alpha = self._s.sentiment_ema_alpha
        new_ema = alpha * sentiment + (1 - alpha) * meta.sentiment_ema
        updated = UserMeta(
            user_id=user_id,
            last_interaction_at=now,
            last_sentiment=sentiment,
            sentiment_ema=new_ema,
            interaction_count=meta.interaction_count + 1,
            relationship_summary=meta.relationship_summary,
            relationship_health=meta.relationship_health,
        )
        self._db.save_user_meta(updated)
        return updated

    def _relationship_context(self, user_id: str) -> UserMeta:
        return self._db.get_user_meta(user_id) or UserMeta(user_id=user_id)

    def _refresh_relationship_insight(
        self,
        user_id: str,
        relationship: Relationship,
        meta: UserMeta,
        sentiment: float,
        session_id: str,
    ) -> RelationshipInsight:
        """更新关系健康度与归纳摘要（LLM 按间隔触发）。"""
        memories = [m.content for m in self._memory.retrieve(user_id, "用户近况", top_k=6)]
        history = self._db.recent_messages(session_id, self._s.recent_messages_window)
        user_lines = [m.content for m in history if m.role == "user"]
        every_n = self._s.relationship_summary_every_n
        use_llm = every_n > 0 and meta.interaction_count % every_n == 0
        insight = build_insight(
            self._llm if use_llm else None,
            self._persona,
            relationship,
            meta.sentiment_ema,
            sentiment,
            meta.interaction_count,
            memories,
            user_lines,
            use_llm=use_llm,
        )
        summary = insight.summary
        if not use_llm and meta.relationship_summary:
            summary = meta.relationship_summary
        final = RelationshipInsight(
            health_score=insight.health_score, summary=summary, trend=insight.trend
        )
        self._db.save_user_meta(
            UserMeta(
                user_id=user_id,
                last_interaction_at=meta.last_interaction_at,
                last_sentiment=meta.last_sentiment,
                sentiment_ema=meta.sentiment_ema,
                interaction_count=meta.interaction_count,
                relationship_summary=final.summary,
                relationship_health=final.health_score,
            )
        )
        return final

    def _appraise_and_relate(
        self, emotion: EmotionState, relationship: Relationship, user_text: str
    ) -> tuple[EmotionState, float, str, Relationship]:
        emotion, sentiment, sent_result = self._emotion_engine.appraise(
            emotion,
            user_text,
            persona=self._persona,
            llm=self._llm,
            sentiment_mode=self._s.sentiment_mode,
        )
        relationship = self._emotion_engine.update_relationship(
            relationship, sentiment, persona=self._persona
        )
        return emotion, sentiment, sent_result.label, relationship

    def _load_state(self, user_id: str) -> tuple[EmotionState, Relationship]:
        emotion = self._db.get_emotion(user_id) or EmotionState()
        relationship = self._db.get_relationship(user_id) or Relationship()
        return emotion, relationship

    def get_state(self, user_id: str) -> tuple[EmotionState, Relationship]:
        return self._load_state(user_id)

    def chat(self, user_id: str, session_id: str, user_text: str) -> ChatResult:
        now = time.time()
        emotion, relationship = self._load_state(user_id)

        # [1] 记录用户消息
        sentiment_for_log = 0.0
        self._db.add_message(
            Message(session_id=session_id, role="user", content=user_text, created_at=now)
        )

        # [2] 安全前置：危机/未成年人内容分级/隐私防诱导，优先于一切
        safety = check_safety(user_text, audience=self._s.audience)
        if safety.is_blocked:
            # 安全事件写入家长可见审计日志
            if self._audit and safety.category:
                self._audit.log_safety_event(user_id, safety.category.value, user_text)
            reply = safety.safe_response or ""
            self._db.add_message(
                Message(session_id=session_id, role="assistant", content=reply, created_at=time.time())
            )
            if safety.is_crisis:
                # 危机事件作为高重要度记忆留存
                self._memory.add(
                    user_id, f"ta 表达了强烈的负面/危机情绪：{user_text}",
                    mem_type=MemoryType.EPISODIC, importance=10.0,
                )
            # 危机记为极低情绪以便后续主动关心；其他拦截记中性
            self._record_interaction(
                user_id, time.time(), -1.0 if safety.is_crisis else 0.0
            )
            avatar = emotion_to_avatar(emotion, is_crisis=safety.is_crisis)
            return ChatResult(
                reply=reply, emotion=emotion, relationship=relationship,
                avatar=avatar, retrieved_memories=[], is_crisis=safety.is_crisis,
                llm="safety",
                safety_category=safety.category.value if safety.category else None,
                tts=self._maybe_tts(
                    reply,
                    emotion,
                    is_crisis=safety.is_crisis,
                    user_sentiment=-1.0 if safety.is_crisis else 0.0,
                ),
            )

        # [3] 记忆检索
        retrieved = self._memory.retrieve(user_id, user_text)
        meta_ctx = self._relationship_context(user_id)

        # [4] 情绪评估 + 关系演化（混合/LLM 情感 + 大五人格调制）
        emotion, sentiment_for_log, sentiment_label, relationship = self._appraise_and_relate(
            emotion, relationship, user_text
        )

        # [5] 构建提示并生成（未成年人受众注入守护守则）
        guard = minor_guard_prompt() if self._s.audience == "minor" else ""
        system_prompt = build_system_prompt(
            self._persona,
            emotion,
            relationship,
            retrieved,
            guard_prompt=guard,
            relationship_summary=meta_ctx.relationship_summary,
        )
        history = [
            {"role": m.role, "content": m.content}
            for m in self._db.recent_messages(session_id, self._s.recent_messages_window)
        ]
        reply = self._llm.generate(system_prompt, history)
        user_texts = [m["content"] for m in history if m["role"] == "user"] + [user_text]
        reply = enforce_memory_honesty(reply, retrieved, user_texts)

        # [6] 状态后处理：持久化情绪/关系、记录回复、沉淀记忆、触发反思
        self._db.save_emotion(user_id, emotion, time.time())
        self._db.save_relationship(user_id, relationship, time.time())
        self._db.add_message(
            Message(session_id=session_id, role="assistant", content=reply, created_at=time.time())
        )

        importance = self._estimate_importance(user_text, sentiment_for_log)
        self._memory.add(user_id, f"ta 说：{user_text}", importance=importance)
        rel_summary = meta_ctx.relationship_summary
        maybe_reflect(
            self._memory,
            user_id,
            self._s.reflection_every_n_memories,
            self._llm,
            self._persona,
            relationship_summary=rel_summary,
        )

        meta = self._record_interaction(user_id, time.time(), sentiment_for_log)
        insight = self._refresh_relationship_insight(
            user_id, relationship, meta, sentiment_for_log, session_id
        )
        for ev in extract_events(user_text, time.time()):
            ev.user_id = user_id
            self._db.add_event(ev)

        # [7] 数字人表情 + 可选 TTS
        avatar = emotion_to_avatar(
            emotion, is_crisis=False, user_sentiment=sentiment_for_log
        )

        return ChatResult(
            reply=reply, emotion=emotion, relationship=relationship,
            avatar=avatar, retrieved_memories=[m.content for m in retrieved],
            is_crisis=False, llm=self._llm.name, safety_category=None,
            tts=self._maybe_tts(
                reply, emotion, is_crisis=False, user_sentiment=sentiment_for_log
            ),
            relationship_summary=insight.summary,
            relationship_health=insight.health_score,
            relationship_trend=insight.trend,
            user_sentiment_label=sentiment_label,
        )

    def chat_stream(
        self, user_id: str, session_id: str, user_text: str
    ) -> Iterator[dict[str, Any]]:
        """流式对话：yield meta → token* → done（含最终校正后全文）。"""
        now = time.time()
        emotion, relationship = self._load_state(user_id)
        self._db.add_message(
            Message(session_id=session_id, role="user", content=user_text, created_at=now)
        )

        safety = check_safety(user_text, audience=self._s.audience)
        if safety.is_blocked:
            if self._audit and safety.category:
                self._audit.log_safety_event(user_id, safety.category.value, user_text)
            reply = safety.safe_response or ""
            self._db.add_message(
                Message(session_id=session_id, role="assistant", content=reply, created_at=time.time())
            )
            if safety.is_crisis:
                self._memory.add(
                    user_id, f"ta 表达了强烈的负面/危机情绪：{user_text}",
                    mem_type=MemoryType.EPISODIC, importance=10.0,
                )
            self._record_interaction(user_id, time.time(), -1.0 if safety.is_crisis else 0.0)
            avatar = emotion_to_avatar(emotion, is_crisis=safety.is_crisis)
            yield self._stream_meta(emotion, relationship, avatar, [], safety.is_crisis)
            yield {"type": "token", "text": reply}
            yield self._stream_done(
                reply, emotion, relationship, avatar, [], safety.is_crisis, "safety", None
            )
            return

        retrieved = self._memory.retrieve(user_id, user_text)
        meta_ctx = self._relationship_context(user_id)
        emotion, sentiment_for_log, sentiment_label, relationship = self._appraise_and_relate(
            emotion, relationship, user_text
        )

        guard = minor_guard_prompt() if self._s.audience == "minor" else ""
        system_prompt = build_system_prompt(
            self._persona,
            emotion,
            relationship,
            retrieved,
            guard_prompt=guard,
            relationship_summary=meta_ctx.relationship_summary,
        )
        history = [
            {"role": m.role, "content": m.content}
            for m in self._db.recent_messages(session_id, self._s.recent_messages_window)
        ]
        user_texts = [m["content"] for m in history if m["role"] == "user"] + [user_text]
        avatar = emotion_to_avatar(
            emotion, is_crisis=False, user_sentiment=sentiment_for_log
        )

        yield self._stream_meta(
            emotion,
            relationship,
            avatar,
            [m.content for m in retrieved],
            False,
            sentiment_label=sentiment_label,
            meta_ctx=meta_ctx,
        )

        parts: list[str] = []
        for piece in self._llm.generate_stream(system_prompt, history):
            parts.append(piece)
            yield {"type": "token", "text": piece}

        reply = enforce_memory_honesty("".join(parts), retrieved, user_texts)

        self._db.save_emotion(user_id, emotion, time.time())
        self._db.save_relationship(user_id, relationship, time.time())
        self._db.add_message(
            Message(session_id=session_id, role="assistant", content=reply, created_at=time.time())
        )
        importance = self._estimate_importance(user_text, sentiment_for_log)
        self._memory.add(user_id, f"ta 说：{user_text}", importance=importance)
        rel_summary = meta_ctx.relationship_summary
        maybe_reflect(
            self._memory,
            user_id,
            self._s.reflection_every_n_memories,
            self._llm,
            self._persona,
            relationship_summary=rel_summary,
        )
        meta = self._record_interaction(user_id, time.time(), sentiment_for_log)
        insight = self._refresh_relationship_insight(
            user_id, relationship, meta, sentiment_for_log, session_id
        )
        for ev in extract_events(user_text, time.time()):
            ev.user_id = user_id
            self._db.add_event(ev)

        yield self._stream_done(
            reply, emotion, relationship, avatar,
            [m.content for m in retrieved], False, self._llm.name, None,
            sentiment_label=sentiment_label,
            insight=insight,
        )

    @staticmethod
    def _relationship_payload(
        relationship: Relationship,
        *,
        health_score: float = 0.0,
        summary: str = "",
        trend: str = "new",
    ) -> dict[str, Any]:
        return {
            "affinity": relationship.affinity,
            "stage": relationship.stage.value,
            "health_score": health_score,
            "summary": summary,
            "trend": trend,
        }

    @staticmethod
    def _stream_meta(
        emotion: EmotionState,
        relationship: Relationship,
        avatar: AvatarCue,
        memories: list[str],
        is_crisis: bool,
        sentiment_label: str = "",
        meta_ctx: UserMeta | None = None,
    ) -> dict[str, Any]:
        health = meta_ctx.relationship_health if meta_ctx else 0.0
        summary = meta_ctx.relationship_summary if meta_ctx else ""
        return {
            "type": "meta",
            "emotion": {
                "pleasure": emotion.pleasure,
                "arousal": emotion.arousal,
                "dominance": emotion.dominance,
                "label": emotion.label(),
            },
            "relationship": Orchestrator._relationship_payload(
                relationship, health_score=health, summary=summary
            ),
            "avatar": {
                "expression": avatar.expression,
                "intensity": avatar.intensity,
                "animation": avatar.animation,
            },
            "retrieved_memories": memories,
            "is_crisis": is_crisis,
            "user_sentiment_label": sentiment_label,
        }

    @staticmethod
    def _stream_done(
        reply: str,
        emotion: EmotionState,
        relationship: Relationship,
        avatar: AvatarCue,
        memories: list[str],
        is_crisis: bool,
        llm: str,
        safety_category: str | None,
        sentiment_label: str = "",
        insight: RelationshipInsight | None = None,
    ) -> dict[str, Any]:
        health = insight.health_score if insight else 0.0
        summary = insight.summary if insight else ""
        trend = insight.trend if insight else "new"
        return {
            "type": "done",
            "reply": reply,
            "emotion": {
                "pleasure": emotion.pleasure,
                "arousal": emotion.arousal,
                "dominance": emotion.dominance,
                "label": emotion.label(),
            },
            "relationship": Orchestrator._relationship_payload(
                relationship, health_score=health, summary=summary, trend=trend
            ),
            "avatar": {
                "expression": avatar.expression,
                "intensity": avatar.intensity,
                "animation": avatar.animation,
            },
            "retrieved_memories": memories,
            "is_crisis": is_crisis,
            "llm": llm,
            "safety_category": safety_category,
            "user_sentiment_label": sentiment_label,
        }

    def _maybe_tts(
        self,
        text: str,
        emotion: EmotionState,
        is_crisis: bool = False,
        user_sentiment: float | None = None,
    ) -> TTSResult | None:
        """按配置在 chat 响应内联 TTS（嵌入游戏时通常关闭，改用 /api/tts 按需取）。

        语音风格随当前情绪变化（开心更快更亮，难过更慢更低，危机更轻柔）。
        """
        if self._tts is None or not self._s.chat_include_tts:
            return None
        style = style_from_emotion(
            emotion, is_crisis=is_crisis, user_sentiment=user_sentiment
        )
        return self._tts.synthesize(text, style=style)

    # ---------- 主动关心 ----------
    def check_proactive(self, user_id: str, now: float | None = None) -> ProactiveResult:
        return self._proactivity.check(user_id, now)

    def deliver_proactive(self, user_id: str, now: float | None = None):
        """评估并"投递"一条主动消息：标记事件已触发、刷新互动时间，返回结果与表情。

        返回 (ProactiveResult, AvatarCue|None)。should_reach_out=False 时 avatar 为 None。
        """
        result = self._proactivity.check(user_id, now)
        if not result.should_reach_out:
            return result, None

        # 主动消息也记入对话历史，并刷新互动时间，避免反复触发
        ts = now or time.time()
        session_id = f"sess-{user_id}"
        self._db.add_message(
            Message(session_id=session_id, role="assistant", content=result.message or "", created_at=ts)
        )
        if result.event_id is not None:
            self._db.mark_event_fired(result.event_id)
        meta = self._db.get_user_meta(user_id) or UserMeta(user_id=user_id)
        self._db.save_user_meta(
            UserMeta(user_id=user_id, last_interaction_at=ts, last_sentiment=meta.last_sentiment)
        )

        emotion, _ = self._load_state(user_id)
        expr_map = {"event": False, "idle": False, "emotion": True}
        avatar = emotion_to_avatar(emotion, is_crisis=expr_map.get(result.trigger, False))
        return result, avatar

    @staticmethod
    def _estimate_importance(text: str, sentiment: float) -> float:
        """情绪强度高、包含关键信息（名字/日期/重要的人）的内容更重要。"""
        importance = 3.0 + abs(sentiment) * 4.0
        cues = ["生日", "面试", "考试", "分手", "妈妈", "爸爸", "工作", "梦想", "名字", "喜欢"]
        if any(c in text for c in cues):
            importance += 2.0
        return min(10.0, importance)

