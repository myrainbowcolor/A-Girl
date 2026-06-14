"""核心领域模型（与存储/传输解耦的纯数据结构）。"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class MemoryType(str, Enum):
    EPISODIC = "episodic"      # 情景记忆：发生过什么
    SEMANTIC = "semantic"      # 语义记忆：关于用户的事实
    REFLECTION = "reflection"  # 反思：高层洞察


class RelationshipStage(str, Enum):
    STRANGER = "stranger"      # 陌生
    ACQUAINTED = "acquainted"  # 熟悉
    FRIEND = "friend"          # 朋友
    CLOSE = "close"            # 亲密


@dataclass
class Persona:
    """稳定人格（慢变量）。"""
    name: str = "小语"
    age: int = 24
    backstory: str = (
        "一个温柔、细腻、善于倾听的女孩，喜欢在夜晚聊天，"
        "会记得你说过的小事，也有自己的小情绪和小爱好。"
    )
    # 大五人格，取值 0~1
    openness: float = 0.7
    conscientiousness: float = 0.6
    extraversion: float = 0.55
    agreeableness: float = 0.85
    neuroticism: float = 0.4
    speaking_style: str = "口语化、亲切、偶尔俏皮，会用'嗯''呀'这类语气词，不堆砌华丽辞藻。"
    values: str = "重视真诚与陪伴，relationships 比输赢更重要。"
    interests: str = "音乐、散步、深夜的对话、记录生活里的小确幸。"
    taboos: str = "不说教、不冷冰冰地讲大道理、不假装无所不知。"


@dataclass
class EmotionState:
    """PAD 三维情绪（连续值，范围约束在 [-1, 1]）。"""
    pleasure: float = 0.2
    arousal: float = 0.0
    dominance: float = 0.0

    def label(self) -> str:
        """将 PAD 映射为可读情绪标签，用于 UI 与语气提示。"""
        p, a, d = self.pleasure, self.arousal, self.dominance
        if p >= 0.55 and a >= 0.5:
            return "开心又有点小兴奋"
        if p >= 0.3 and a >= 0.3:
            return "开心，心里暖暖的"
        if p >= 0.3 and a < 0.3:
            return "平静又满足"
        if p <= -0.3 and a >= 0.5:
            return "有些焦虑/委屈"
        if p <= -0.3 and d < -0.1:
            return "低落，想轻轻安慰你"
        if p <= -0.3:
            return "低落"
        if a >= 0.55:
            return "有点惊讶/好奇"
        return "平和"


@dataclass
class Relationship:
    """关系状态（慢变量）。"""
    affinity: float = 5.0  # 0~100
    stage: RelationshipStage = RelationshipStage.STRANGER

    def recompute_stage(self) -> None:
        if self.affinity >= 70:
            self.stage = RelationshipStage.CLOSE
        elif self.affinity >= 40:
            self.stage = RelationshipStage.FRIEND
        elif self.affinity >= 15:
            self.stage = RelationshipStage.ACQUAINTED
        else:
            self.stage = RelationshipStage.STRANGER


@dataclass
class Memory:
    user_id: str
    content: str
    type: MemoryType = MemoryType.EPISODIC
    importance: float = 3.0  # 1~10
    embedding: list[float] = field(default_factory=list)
    created_at: float = 0.0
    last_access: float = 0.0
    id: Optional[int] = None


@dataclass
class Message:
    session_id: str
    role: str  # user | assistant
    content: str
    sentiment: float = 0.0  # -1~1
    created_at: float = 0.0
    id: Optional[int] = None


@dataclass
class UserMeta:
    """用于主动关心与关系归纳的轻量元信息。"""
    user_id: str
    last_interaction_at: float = 0.0
    last_sentiment: float = 0.0
    sentiment_ema: float = 0.0          # 情感指数滑动平均 [-1, 1]
    interaction_count: int = 0
    relationship_summary: str = ""    # LLM/规则归纳的关系描述
    relationship_health: float = 0.0  # 0~100 关系健康度
    user_behavior: str = ""           # 行为模式分析
    user_intent: str = ""             # 当前意图
    user_state: str = ""              # 当前状态
    user_speaking_style: str = ""     # 说话方式（跨轮累积）
    user_thought_pattern: str = ""    # 思想/思维倾向
    user_profile_summary: str = ""    # 综合用户画像
    proactive_topic: str = ""         # 建议主动跟进话题
    insight_turn_count: int = 0       # 洞察更新次数（LLM 深描节奏）
    last_insight_at: float = 0.0
    last_proactive_at: float = 0.0    # 上次主动消息时间（冷却）


@dataclass
class Event:
    """重要事件（用于事件触发的主动关心），如生日/面试/考试。"""
    user_id: str
    kind: str          # birthday | interview | exam | other
    label: str         # 原始描述
    trigger_at: float  # 触发时间戳
    created_at: float = 0.0
    fired: bool = False
    id: Optional[int] = None
