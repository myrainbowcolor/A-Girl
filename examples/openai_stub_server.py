"""OpenAI 兼容桩服务（开发/验证用）。

模拟 OpenAI 兼容的 /chat/completions、/audio/speech、/audio/transcriptions，
用于在没有真实 API Key 时验证 A-Girl 的"填 AGIRL_LLM_* / AGIRL_VOICE_* 即切换"链路。

运行：
    python -m uvicorn examples.openai_stub_server:app --host 127.0.0.1 --port 9000

再让 A-Girl 指向它：
    AGIRL_LLM_PROVIDER=openai_compatible \
    AGIRL_LLM_BASE_URL=http://127.0.0.1:9000/v1 \
    AGIRL_LLM_API_KEY=test AGIRL_LLM_MODEL=stub-model \
    python -m uvicorn app.main:app --port 8011
"""
from __future__ import annotations

import io
import struct

from fastapi import FastAPI, Request
from fastapi.responses import Response

app = FastAPI(title="OpenAI Stub Server")


@app.post("/v1/chat/completions")
async def chat_completions(req: Request) -> dict:
    body = await req.json()
    messages = body.get("messages", [])
    user_last = next((m["content"] for m in reversed(messages) if m.get("role") == "user"), "")
    reply = f"[stub-llm] 我收到你说的：{user_last}。这是来自 OpenAI 兼容桩服务的回复。"
    return {
        "id": "stub-1",
        "object": "chat.completion",
        "model": body.get("model", "stub-model"),
        "choices": [{"index": 0, "message": {"role": "assistant", "content": reply}, "finish_reason": "stop"}],
        "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
    }


@app.post("/v1/audio/speech")
async def audio_speech(req: Request) -> Response:
    body = await req.json()
    text = body.get("input", "")
    # 返回合法静音 WAV
    n = max(1600, len(text) * 1600)
    buf = io.BytesIO()
    buf.write(b"RIFF"); buf.write(struct.pack("<I", 36 + n * 2)); buf.write(b"WAVE")
    buf.write(b"fmt "); buf.write(struct.pack("<IHHIIHH", 16, 1, 1, 16000, 32000, 2, 16))
    buf.write(b"data"); buf.write(struct.pack("<I", n * 2)); buf.write(b"\x00\x00" * n)
    return Response(content=buf.getvalue(), media_type="audio/wav")


@app.post("/v1/audio/transcriptions")
async def audio_transcriptions() -> dict:
    return {"text": "[stub-stt] 这是桩服务的语音转写结果。"}
