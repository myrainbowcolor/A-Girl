"""pytest 全局：测试与 CI 固定使用 mock LLM，不依赖外部 API。"""
from __future__ import annotations

import os

# 必须在 import app.main 之前生效
os.environ.setdefault("AGIRL_LLM_PROVIDER", "mock")
os.environ.setdefault("AGIRL_TTS_PROVIDER", "mock")
os.environ.setdefault("AGIRL_STT_PROVIDER", "mock")
