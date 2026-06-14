"""运行配置。

通过环境变量覆盖默认值；无任何 Key 时退化为可离线运行的 mock 模式，
保证骨架在没有外部依赖的情况下也能完整跑通与测试。
"""
from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="AGIRL_", env_file=".env", extra="ignore")

    # LLM provider：mock | openai_compatible
    llm_provider: str = "mock"
    llm_base_url: str = "https://api.openai.com/v1"
    llm_api_key: str = ""
    llm_model: str = "gpt-4o-mini"
    llm_timeout_seconds: float = 180.0   # 本地 Llama 首 token 可能较慢
    llm_reply_temperature: float = 0.72  # 对话生成温度（略低更口语、少跑题）

    # Embedding provider：hash | openai_compatible
    embedding_provider: str = "hash"
    embedding_model: str = "text-embedding-3-small"
    embedding_dim: int = 256

    # 语音 provider：mock | edge（免费） | openai_compatible
    tts_provider: str = "edge"
    stt_provider: str = "mock"
    voice_base_url: str = "https://api.openai.com/v1"
    voice_api_key: str = ""
    tts_model: str = "tts-1"
    tts_voice: str = "alloy"
    # Edge TTS 免费中文音色（晓晓=温柔女声，晓伊=活泼女声）
    edge_tts_voice: str = "zh-CN-XiaoxiaoNeural"
    stt_model: str = "whisper-1"
    # 是否在 /api/chat 响应中内联 TTS 音频（嵌入游戏时可关以省带宽，改用 /api/tts 按需取）
    chat_include_tts: bool = False

    # 受众：minor（未成年人，默认强化安全）| general
    audience: str = "minor"

    # 部署模式：standalone（自带 Web UI）| embedded（仅 API，供游戏调用）
    deployment_mode: str = "standalone"

    # 主动关心调度
    proactive_idle_seconds: int = 6 * 3600        # 闲置多久后主动问候
    proactive_event_window_seconds: int = 86400   # 事件到点前后多久内触发
    proactive_scheduler_enabled: bool = False     # 是否启用后台轮询调度
    proactive_scheduler_interval_seconds: int = 60

    # 主动推送：webhook 回调地址（留空则仅 SSE）
    push_webhook_url: str = ""

    # 未成年人合规
    require_age_gate: bool = True                 # 是否需要年龄确认后才能对话
    min_age: int = 0                              # 允许的最小年龄（0=不限，仅记录）
    audit_log_path: str = "audit.log"             # 家长可见安全审计日志路径

    # 持久化：SQLite 文件路径
    db_path: str = "agirl.db"

    # 记忆检索权重
    memory_weight_relevance: float = 1.0
    memory_weight_recency: float = 0.6
    memory_weight_importance: float = 0.9
    memory_top_k: int = 5

    # 反思触发：每累计 N 条新记忆触发一次反思
    reflection_every_n_memories: int = 8

    # 记忆检索：最低相关度（哈希 embedding 下过滤弱相关，减少误召回）
    memory_min_relevance: float = 0.12

    # 近期对话注入轮数
    recent_messages_window: int = 6

    # 情感分析：lexicon | llm | hybrid（中性句用 LLM 细判；lexicon 最快）
    sentiment_mode: str = "lexicon"
    sentiment_ema_alpha: float = 0.35   # 情感 EMA 平滑系数

    # 关系归纳：每 N 轮互动刷新一次 LLM 关系摘要（0=仅规则；越大越少调 LLM）
    relationship_summary_every_n: int = 6

    # 用户洞察驱动的主动沟通
    proactive_insight_enabled: bool = True
    proactive_insight_min_idle_seconds: int = 1800   # 至少闲置 30 分钟再洞察触发
    proactive_insight_cooldown_seconds: int = 3600     # 洞察主动消息冷却 1 小时
    proactive_insight_min_confidence: float = 0.55
    user_insight_use_llm: bool = False                 # 对话路径用规则分析，避免额外 LLM
    user_insight_history_limit: int = 40             # 洞察分析拉取的用户消息条数
    user_insight_llm_every_n: int = 2                  # 启用 LLM 时每 N 次洞察做一次深描
    user_insight_min_messages: int = 2                 # 至少 N 条用户消息才输出深度画像

    # 流式对话：done 事件前是否推迟反思/关系归纳等重型 LLM 任务到后台
    chat_defer_heavy_post: bool = True


@lru_cache
def get_settings() -> Settings:
    return Settings()
