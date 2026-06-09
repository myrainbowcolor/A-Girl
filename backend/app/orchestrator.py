"""对话编排：串联感知 → 安全 → 记忆检索 → 情绪评估 → 生成 → 状态更新。"""
from __future__ import annotations

import time
from dataclasses import dataclass

from .config import Settings
from .db import Database
from .domain import EmotionState, MemoryType, Message, Persona, Relationship
from .emotion import EmotionEngine
from .llm import LLMProvider
from .memory import MemoryStore
from .persona import build_system_prompt, default_persona
from .safety import check_safety


@dataclass
class ChatResult:
    reply: str
    emotion: EmotionState
    relationship: Relationship
    retrieved_memories: list[str]
    is_crisis: bool
    llm: str


class Orchestrator:
    def __init__(
        self,
        db: Database,
        memory: MemoryStore,
        emotion_engine: EmotionEngine,
        llm: LLMProvider,
        settings: Settings,
        persona: Persona | None = None,
    ) -> None:
        self._db = db
        self._memory = memory
        self._emotion_engine = emotion_engine
        self._llm = llm
        self._s = settings
        self._persona = persona or default_persona()

    @property
    def persona(self) -> Persona:
        return self._persona

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

        # [2] 安全前置：危机检测优先于一切
        safety = check_safety(user_text)
        if safety.is_crisis:
            reply = safety.safe_response or ""
            self._db.add_message(
                Message(session_id=session_id, role="assistant", content=reply, created_at=time.time())
            )
            # 危机事件作为高重要度记忆留存
            self._memory.add(
                user_id, f"ta 表达了强烈的负面/危机情绪：{user_text}",
                mem_type=MemoryType.EPISODIC, importance=10.0,
            )
            return ChatResult(
                reply=reply, emotion=emotion, relationship=relationship,
                retrieved_memories=[], is_crisis=True, llm="safety",
            )

        # [3] 记忆检索
        retrieved = self._memory.retrieve(user_id, user_text)

        # [4] 情绪评估 + 关系演化
        emotion, sentiment_for_log = self._emotion_engine.appraise(emotion, user_text)
        relationship = self._emotion_engine.update_relationship(relationship, sentiment_for_log)

        # [5] 构建提示并生成
        system_prompt = build_system_prompt(self._persona, emotion, relationship, retrieved)
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

        return ChatResult(
            reply=reply, emotion=emotion, relationship=relationship,
            retrieved_memories=[m.content for m in retrieved],
            is_crisis=False, llm=self._llm.name,
        )

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
