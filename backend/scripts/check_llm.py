#!/usr/bin/env python3
"""检查当前 LLM 配置是否可用（Mock / Ollama / OpenAI 兼容）。"""
from __future__ import annotations

import sys

from app.config import get_settings
from app.llm import build_llm_provider


def main() -> int:
    s = get_settings()
    llm = build_llm_provider(s)
    print(f"provider: {llm.name}")
    print(f"config:   AGIRL_LLM_PROVIDER={s.llm_provider}")
    print(f"          AGIRL_LLM_BASE_URL={s.llm_base_url}")
    print(f"          AGIRL_LLM_MODEL={s.llm_model}")

    if llm.name == "mock":
        print("\n[警告] 仍在 Mock 模式（机械回复）。")
        print("  请在 backend/.env 配置 Ollama，或运行 scripts/setup-ollama.ps1")
        return 1

    try:
        reply = llm.generate(
            "你是小语，说话口语化。",
            [{"role": "user", "content": "我很烦，用一句话安慰我"}],
            temperature=0.8,
        )
        print(f"\n[OK] 测试回复:\n{reply}\n")
        return 0
    except Exception as e:
        print(f"\n[失败] LLM 调用出错: {e}")
        print("  确认 Ollama 已启动: curl http://127.0.0.1:11434/api/tags")
        return 2


if __name__ == "__main__":
    sys.exit(main())
