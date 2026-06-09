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
    llm_timeout_seconds: float = 30.0

    # Embedding provider：hash | openai_compatible
    embedding_provider: str = "hash"
    embedding_model: str = "text-embedding-3-small"
    embedding_dim: int = 256

    # 语音 provider：mock | openai_compatible（base_url 可指向自托管语音服务）
    tts_provider: str = "mock"
    stt_provider: str = "mock"
    voice_base_url: str = "https://api.openai.com/v1"
    voice_api_key: str = ""
    tts_model: str = "tts-1"
    tts_voice: str = "alloy"
    stt_model: str = "whisper-1"
    # 是否在 /api/chat 响应中内联 TTS 音频（嵌入游戏时可关以省带宽，改用 /api/tts 按需取）
    chat_include_tts: bool = False

    # 受众：minor（未成年人，默认强化安全）| general
    audience: str = "minor"

    # 部署模式：standalone（自带 Web UI）| embedded（仅 API，供游戏调用）
    deployment_mode: str = "standalone"

    # 持久化：SQLite 文件路径
    db_path: str = "agirl.db"

    # 记忆检索权重
    memory_weight_relevance: float = 1.0
    memory_weight_recency: float = 0.6
    memory_weight_importance: float = 0.9
    memory_top_k: int = 5

    # 反思触发：每累计 N 条新记忆触发一次反思
    reflection_every_n_memories: int = 8

    # 近期对话注入轮数
    recent_messages_window: int = 8


@lru_cache
def get_settings() -> Settings:
    return Settings()
