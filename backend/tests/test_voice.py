import base64

from app.voice import MockSTTProvider, MockTTSProvider


def test_mock_tts_returns_valid_wav():
    tts = MockTTSProvider()
    result = tts.synthesize("你好呀")
    assert result.format == "wav"
    assert result.duration_ms >= 300
    raw = base64.b64decode(result.audio_base64)
    # RIFF/WAVE 头校验，保证前端可播放
    assert raw[:4] == b"RIFF"
    assert raw[8:12] == b"WAVE"


def test_mock_tts_duration_scales_with_length():
    tts = MockTTSProvider()
    short = tts.synthesize("嗨")
    long = tts.synthesize("这是一段明显更长的文本用来测试时长估算是否随长度增长")
    assert long.duration_ms > short.duration_ms


def test_mock_stt_returns_text():
    stt = MockSTTProvider()
    text = stt.transcribe("AAAA", fmt="wav")
    assert isinstance(text, str) and len(text) > 0
