from app.avatar import emotion_to_avatar
from app.domain import EmotionState
from app.voice import MockTTSProvider
from app.voice.lipsync import estimate_syllables, generate_lipsync


def test_lipsync_starts_and_ends_closed():
    frames = generate_lipsync("你好呀小语", 1000)
    assert frames[0]["v"] == 0.0
    assert frames[-1]["v"] == 0.0
    assert len(frames) >= 3


def test_lipsync_values_in_range():
    for f in generate_lipsync("今天天气真好我们聊聊天吧", 2000):
        assert 0.0 <= f["v"] <= 1.0
        assert f["t"] >= 0


def test_lipsync_deterministic():
    assert generate_lipsync("你好", 800) == generate_lipsync("你好", 800)


def test_syllable_estimate():
    assert estimate_syllables("你好") == 2
    assert estimate_syllables("hello world") == 2


def test_tts_includes_lipsync():
    result = MockTTSProvider().synthesize("你好呀")
    assert result.lipsync
    assert result.lipsync[0]["v"] == 0.0


def test_avatar_live2d_params():
    cue = emotion_to_avatar(EmotionState(pleasure=0.7, arousal=0.1))  # 微笑
    params = cue.live2d_params()
    assert "ParamMouthForm" in params
    assert params["ParamMouthForm"] > 0  # 微笑嘴角上扬
    sad = emotion_to_avatar(EmotionState(pleasure=-0.6, arousal=0.1)).live2d_params()
    assert sad["ParamMouthForm"] < 0  # 难过嘴角下撇
