"""本机 Llama3 OpenAI 兼容服务（Cloud Agent / 无 Ollama 时用 llama-cpp-python）。

Ollama 在部分容器环境会 segfault，此服务直接加载 GGUF 推理。

运行：
    pip install llama-cpp-python
    export LLAMA_GGUF_PATH=/path/to/model.gguf
    python -m uvicorn examples.llama_cpp_server:app --host 127.0.0.1 --port 11435

A-Girl 配置（backend/.env）：
    AGIRL_LLM_PROVIDER=openai_compatible
    AGIRL_LLM_BASE_URL=http://127.0.0.1:11435/v1
    AGIRL_LLM_API_KEY=local
    AGIRL_LLM_MODEL=llama3
"""
from __future__ import annotations

import os
from functools import lru_cache

from fastapi import FastAPI, Request

app = FastAPI(title="Llama.cpp OpenAI Compatible Server")

_DEFAULT_GGUF = os.environ.get(
    "LLAMA_GGUF_PATH",
    "/home/ubuntu/.ollama/models/blobs/sha256-6a0746a1ec1aef3e7ec53868f220ff6e389f6f8ef87a01d77c96807de94ca2aa",
)
_THREADS = int(os.environ.get("LLAMA_THREADS", "4"))
_CTX = int(os.environ.get("LLAMA_CTX", "4096"))


@lru_cache
def _llm():
    from llama_cpp import Llama

    if not os.path.isfile(_DEFAULT_GGUF):
        raise FileNotFoundError(
            f"GGUF 不存在: {_DEFAULT_GGUF}。请设置 LLAMA_GGUF_PATH 或 ollama pull llama3"
        )
    return Llama(model_path=_DEFAULT_GGUF, n_ctx=_CTX, n_threads=_THREADS, verbose=False)


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "gguf": _DEFAULT_GGUF, "exists": os.path.isfile(_DEFAULT_GGUF)}


@app.post("/v1/chat/completions")
async def chat_completions(req: Request) -> dict:
    body = await req.json()
    messages = body.get("messages", [])
    temperature = float(body.get("temperature", 0.8))
    llm = _llm()
    result = llm.create_chat_completion(
        messages=messages,
        temperature=temperature,
        max_tokens=int(body.get("max_tokens", 256)),
    )
    content = result["choices"][0]["message"]["content"]
    return {
        "id": "llama-cpp-1",
        "object": "chat.completion",
        "model": body.get("model", "llama3"),
        "choices": [
            {
                "index": 0,
                "message": {"role": "assistant", "content": content.strip()},
                "finish_reason": "stop",
            }
        ],
        "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
    }
