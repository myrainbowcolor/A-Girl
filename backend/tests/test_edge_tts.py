import base64
from unittest.mock import AsyncMock, patch

import pytest

from app.voice.edge_tts import EdgeTTSProvider, _mp3_duration_ms


@pytest.fixture
def fake_mp3():
    # 最小 MP3 帧头 + 填充（mutagen 可能无法解析，走 fallback）
    return b"\xff\xfb\x90\x00" + b"\x00" * 200


async def _fake_stream(*_a, **_k):
    yield {"type": "audio", "data": b"\xff\xfb\x90\x00" + b"\x00" * 400}


def test_edge_tts_provider_synthesize(fake_mp3):
    provider = EdgeTTSProvider(voice="zh-CN-XiaoxiaoNeural")
    mock_comm = AsyncMock()
    mock_comm.stream = _fake_stream

    with patch("edge_tts.Communicate", return_value=mock_comm):
        result = provider.synthesize("你好呀小语")

    assert result.format == "mp3"
    assert result.provider == "edge:zh-CN-XiaoxiaoNeural"
    assert result.audio_base64
    assert result.duration_ms >= 300
    assert result.visemes
    raw = base64.b64decode(result.audio_base64)
    assert len(raw) > 10


def test_mp3_duration_fallback():
    ms = _mp3_duration_ms(b"not-mp3", "你好呀", 1.0)
    assert ms >= 300


def test_build_tts_edge_factory():
    from app.config import Settings
    from app.voice import build_tts_provider

    s = Settings(tts_provider="edge", edge_tts_voice="zh-CN-XiaoyiNeural")
    p = build_tts_provider(s)
    assert "edge" in p.name
