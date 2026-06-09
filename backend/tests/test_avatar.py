from app.avatar import emotion_to_avatar
from app.domain import EmotionState


def test_happy_high_arousal_cheers():
    cue = emotion_to_avatar(EmotionState(pleasure=0.7, arousal=0.7))
    assert cue.expression == "大笑"
    assert cue.animation == "cheer"


def test_happy_calm_smiles():
    cue = emotion_to_avatar(EmotionState(pleasure=0.6, arousal=0.1))
    assert cue.expression == "微笑"


def test_sad_low_arousal():
    cue = emotion_to_avatar(EmotionState(pleasure=-0.6, arousal=0.1))
    assert cue.expression == "难过"


def test_crisis_overrides_to_worried_comfort():
    cue = emotion_to_avatar(EmotionState(pleasure=0.9, arousal=0.9), is_crisis=True)
    assert cue.expression == "担心"
    assert cue.animation == "comfort"


def test_intensity_in_range():
    cue = emotion_to_avatar(EmotionState(pleasure=0.5, arousal=0.5))
    assert 0.0 <= cue.intensity <= 1.0


def test_avatar_comfort_when_user_distressed():
    cue = emotion_to_avatar(EmotionState(pleasure=-0.2, arousal=0.3), user_sentiment=-1.0)
    assert cue.expression == "担心"
    assert cue.animation == "comfort"
