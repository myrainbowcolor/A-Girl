"""对话编排：串联感知 → 安全 → 记忆检索 → 情绪评估 → 生成 → 状态更新。"""
from __future__ import annotations

import time
from dataclasses import dataclass

from .avatar import AvatarCue, emotion_to_avatar
from .config import Settings
from .db import Database
from .domain import EmotionState, MemoryType, Message, Persona, Relationship, UserMeta
from .emotion import EmotionEngine
from .llm import LLMProvider
from .memory import MemoryStore
from .persona import build_system_prompt, default_persona
from .proactivity import ProactiveResult, ProactivityEngine, extract_events
from .safety import SafetyCategory, check_safety, minor_guard_prompt
from .voice import TTSProvider
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
    ) -> None:
        self._db = db
        self._memory = memory
        self._emotion_engine = emotion_engine
        self._llm = llm
        self._s = settings
        self._persona = persona or default_persona()
        self._tts = tts
        self._proactivity = ProactivityEngine(db, settings, self._persona)

    @property
    def persona(self) -> Persona:
        return self._persona

    def _record_interaction(self, user_id: str, now: float, sentiment: float) -> None:
        self._db.save_user_meta(
            UserMeta(user_id=user_id, last_interaction_at=now, last_sentiment=sentiment)
        )

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
                tts=self._maybe_tts(reply),
            )

        # [3] 记忆检索
        retrieved = self._memory.retrieve(user_id, user_text)

        # [4] 情绪评估 + 关系演化
        emotion, sentiment_for_log = self._emotion_engine.appraise(emotion, user_text)
        relationship = self._emotion_engine.update_relationship(relationship, sentiment_for_log)

        # [5] 构建提示并生成（未成年人受众注入守护守则）
        guard = minor_guard_prompt() if self._s.audience == "minor" else ""
        system_prompt = build_system_prompt(
            self._persona, emotion, relationship, retrieved, guard_prompt=guard
        )
        history = [
            {"role": m.role, "content": m.content}
            for m in self._db.recent_messages(session_id, self._s.recent_messages_window)
        ]
        reply = self._llm.generate(system_prompt, history)

        # [6] 状态后处理：持久化情绪/关系、记录回复、沉淀记忆、触发反思
        self._db.save_emotion(user_id, emotion, time.time())
        self._db.save_relationship(user_id, relationship, time.time())
        self._db.add_message(
            Message(session_id=session_id, role="assistant", content=reply, created_at=time.time())
        )

        importance = self._estimate_importance(user_text, sentiment_for_log)
        self._memory.add(user_id, f"ta 说：{user_text}", importance=importance)
        self._maybe_reflect(user_id)

        # 记录互动元信息 + 抽取重要事件（供主动关心）
        self._record_interaction(user_id, time.time(), sentiment_for_log)
        for ev in extract_events(user_text, time.time()):
            ev.user_id = user_id
            self._db.add_event(ev)

        # [7] 数字人表情 + 可选 TTS
        avatar = emotion_to_avatar(emotion, is_crisis=False)

        return ChatResult(
            reply=reply, emotion=emotion, relationship=relationship,
            avatar=avatar, retrieved_memories=[m.content for m in retrieved],
            is_crisis=False, llm=self._llm.name, safety_category=None,
            tts=self._maybe_tts(reply),
        )

    def _maybe_tts(self, text: str) -> TTSResult | None:
        """按配置在 chat 响应内联 TTS（嵌入游戏时通常关闭，改用 /api/tts 按需取）。"""
        if self._tts is None or not self._s.chat_include_tts:
            return None
        return self._tts.synthesize(text)

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

    def _maybe_reflect(self, user_id: str) -> None:
        """每累计 N 条记忆，生成一条高层反思（骨架：基于统计的简单总结）。"""
        n = self._s.reflection_every_n_memories
        if n <= 0:
            return
        count = self._memory.count(user_id)
        if count > 0 and count % n == 0:
            recent = self._memory.retrieve(user_id, "最近发生的事和 ta 的状态", top_k=n)
            joined = "；".join(m.content for m in recent)
            insight = f"对最近互动的总结：{joined}"
            self._memory.add(
                user_id, insight, mem_type=MemoryType.REFLECTION, importance=8.0
            )
