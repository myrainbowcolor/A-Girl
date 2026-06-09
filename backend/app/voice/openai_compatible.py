"""OpenAI 兼容语音 Provider（可指向自托管服务）。

TTS：POST {base_url}/audio/speech
STT：POST {base_url}/audio/transcriptions
"""
from __future__ import annotations

import base64

import httpx

from .base import STTProvider, TTSProvider, TTSResult
from .lipsync import generate_lipsync

_MS_PER_CHAR = 140


class OpenAICompatibleTTSProvider(TTSProvider):
    def __init__(self, base_url: str, api_key: str, model: str, voice: str, timeout: float = 30.0) -> None:
        self._base_url = base_url.rstrip("/")
        self._api_key = api_key
        self._model = model
        self._voice = voice
        self._timeout = timeout

    @property
    def name(self) -> str:
        return f"openai_compatible:{self._model}"

    def synthesize(self, text: str, voice: str | None = None) -> TTSResult:
        payload = {
            "model": self._model,
            "voice": voice or self._voice,
            "input": text,
            "response_format": "wav",
        }
        headers = {"Authorization": f"Bearer {self._api_key}", "Content-Type": "application/json"}
        with httpx.Client(timeout=self._timeout) as client:
            resp = client.post(f"{self._base_url}/audio/speech", json=payload, headers=headers)
            resp.raise_for_status()
            audio = resp.content
        duration_ms = max(300, len(text) * _MS_PER_CHAR)
        return TTSResult(
            audio_base64=base64.b64encode(audio).decode("ascii"),
            format="wav",
            duration_ms=duration_ms,
            provider=self.name,
            lipsync=generate_lipsync(text, duration_ms),
        )


class OpenAICompatibleSTTProvider(STTProvider):
    def __init__(self, base_url: str, api_key: str, model: str, timeout: float = 30.0) -> None:
        self._base_url = base_url.rstrip("/")
        self._api_key = api_key
        self._model = model
        self._timeout = timeout

    @property
    def name(self) -> str:
        return f"openai_compatible:{self._model}"

    def transcribe(self, audio_base64: str, fmt: str = "wav") -> str:
        audio = base64.b64decode(audio_base64)
        files = {"file": (f"audio.{fmt}", audio, f"audio/{fmt}")}
        data = {"model": self._model}
        headers = {"Authorization": f"Bearer {self._api_key}"}
        with httpx.Client(timeout=self._timeout) as client:
            resp = client.post(
                f"{self._base_url}/audio/transcriptions", data=data, files=files, headers=headers
            )
            resp.raise_for_status()
            return resp.json().get("text", "").strip()
