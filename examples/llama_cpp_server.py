"""本机 Llama3 OpenAI 兼容服务（Cloud Agent / 无 Ollama 时用 llama-cpp-python）。"""
from __future__ import annotations

import json
import os
from functools import lru_cache

from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse

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
        raise FileNotFoundError(f"GGUF 不存在: {_DEFAULT_GGUF}")
    return Llama(model_path=_DEFAULT_GGUF, n_ctx=_CTX, n_threads=_THREADS, verbose=False)


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "gguf": _DEFAULT_GGUF, "exists": os.path.isfile(_DEFAULT_GGUF)}


def _chunk(content: str, model: str) -> str:
    payload = {
        "id": "llama-cpp-chunk",
        "object": "chat.completion.chunk",
        "model": model,
        "choices": [{"index": 0, "delta": {"content": content}, "finish_reason": None}],
    }
    return f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"


@app.post("/v1/chat/completions")
async def chat_completions(req: Request):
    body = await req.json()
    messages = body.get("messages", [])
    temperature = float(body.get("temperature", 0.8))
    model = body.get("model", "llama3")
    stream = bool(body.get("stream"))
    llm = _llm()

    if stream:

        def gen():
            for chunk in llm.create_chat_completion(
                messages=messages,
                temperature=temperature,
                max_tokens=int(body.get("max_tokens", 256)),
                stream=True,
            ):
                choices = chunk.get("choices") or []
                if not choices:
                    continue
                delta = choices[0].get("delta") or {}
                piece = delta.get("content")
                if piece:
                    yield _chunk(piece, model)
            yield "data: [DONE]\n\n"

        return StreamingResponse(gen(), media_type="text/event-stream")

    result = llm.create_chat_completion(
        messages=messages,
        temperature=temperature,
        max_tokens=int(body.get("max_tokens", 256)),
    )
    content = result["choices"][0]["message"]["content"]
    return {
        "id": "llama-cpp-1",
        "object": "chat.completion",
        "model": model,
        "choices": [
            {
                "index": 0,
                "message": {"role": "assistant", "content": content.strip()},
                "finish_reason": "stop",
            }
        ],
        "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
    }
