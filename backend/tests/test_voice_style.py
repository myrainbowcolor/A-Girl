from app.domain import EmotionState
from app.voice import MockTTSProvider, VoiceStyle, style_from_emotion
from app.voice.lipsync import VISEME_SHAPES, generate_visemes, text_to_visemes


def test_happy_style_faster_higher():
    s = style_from_emotion(EmotionState(pleasure=0.7, arousal=0.6))
    assert s.rate > 1.0 and s.pitch > 1.0
    assert s.style in ("excited", "cheerful")


def test_sad_style_slower_lower():
    s = style_from_emotion(EmotionState(pleasure=-0.6, arousal=-0.2))
    assert s.rate < 1.0
    assert s.style == "sad"


def test_crisis_style_gentle():
    s = style_from_emotion(EmotionState(pleasure=0.5, arousal=0.5), is_crisis=True)
    assert s.style == "gentle"
    assert s.rate < 1.0


def test_distressed_user_softens_voice():
    base = style_from_emotion(EmotionState(pleasure=0.5, arousal=0.5))
    soft = style_from_emotion(EmotionState(pleasure=0.5, arousal=0.5), user_sentiment=-0.8)
    assert soft.rate < base.rate
    assert soft.style == "gentle"


def test_positive_user_warms_voice():
    base = style_from_emotion(EmotionState(pleasure=0.1, arousal=0.1))
    warm = style_from_emotion(EmotionState(pleasure=0.1, arousal=0.1), user_sentiment=0.7)
    assert warm.rate >= base.rate
    assert warm.pitch >= base.pitch


def test_style_bounds():
    s = style_from_emotion(EmotionState(pleasure=1.0, arousal=1.0))
    assert 0.6 <= s.rate <= 1.4 and 0.7 <= s.pitch <= 1.35


def test_tts_carries_style_and_visemes():
    r = MockTTSProvider().synthesize("你好呀", style=style_from_emotion(EmotionState(pleasure=0.8, arousal=0.5)))
    assert r.style and r.style["style"] in ("excited", "cheerful")
    assert r.visemes and "viseme" in r.visemes[1]


def test_faster_rate_shorter_audio():
    fast = MockTTSProvider().synthesize("这是一段测试文本", style=VoiceStyle(rate=1.4))
    slow = MockTTSProvider().synthesize("这是一段测试文本", style=VoiceStyle(rate=0.7))
    assert fast.duration_ms < slow.duration_ms


def test_visemes_start_end_rest():
    frames = generate_visemes("你好呀小语", 1500)
    assert frames[0]["viseme"] == "REST"
    assert frames[-1]["viseme"] == "REST"
    assert all(0.0 <= f["open"] <= 1.0 for f in frames)


def test_text_to_visemes_vowels():
    vs = text_to_visemes("aeiou")
    assert vs == ["A", "E", "I", "O", "U"]


def test_text_to_visemes_deterministic_cjk():
    assert text_to_visemes("小语") == text_to_visemes("小语")
    assert all(v in VISEME_SHAPES for v in text_to_visemes("今天好开心"))
