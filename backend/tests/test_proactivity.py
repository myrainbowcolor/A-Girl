import tempfile
import time

import pytest

from app.config import Settings
from app.db import Database
from app.domain import Message, Persona, Relationship, UserMeta
from app.proactivity import ProactivityEngine, extract_events


@pytest.fixture
def engine():
    with tempfile.NamedTemporaryFile(suffix=".db") as f:
        db = Database(f.name)
        s = Settings(
            db_path=f.name,
            proactive_idle_seconds=45 * 60,
            proactive_warm_idle_seconds=8 * 60,
            proactive_emotion_min_idle_seconds=10 * 60,
            proactive_global_cooldown_seconds=12 * 60,
            proactive_insight_enabled=True,
            proactive_insight_min_idle_seconds=5 * 60,
            proactive_insight_cooldown_seconds=15 * 60,
            proactive_insight_min_confidence=0.48,
            user_insight_use_llm=False,
        )
        yield ProactivityEngine(db, s, Persona()), db, s
        db.close()


def test_welcome_trigger_on_first_visit(engine):
    eng, _, _ = engine
    r = eng.check("u1")
    assert r.should_reach_out and r.trigger == "welcome"
    assert "嗨" in (r.message or "")


def test_no_trigger_without_meta_when_has_history(engine):
    eng, db, _ = engine
    from app.domain import Message
    db.add_message(Message(session_id="sess-u1", role="user", content="hi", created_at=time.time()))
    assert not eng.check("u1").should_reach_out


def _seed_history(db, user_id: str = "u1") -> None:
    db.add_message(
        Message(session_id=f"sess-{user_id}", role="user", content="之前聊过", created_at=time.time())
    )


def test_idle_trigger(engine):
    eng, db, s = engine
    _seed_history(db)
    now = time.time()
    db.save_user_meta(UserMeta("u1", last_interaction_at=now - s.proactive_idle_seconds - 60, last_sentiment=0.1))
    r = eng.check("u1", now=now)
    assert r.should_reach_out and r.trigger == "idle"
    assert r.message


def test_warm_trigger(engine):
    eng, db, s = engine
    _seed_history(db)
    now = time.time()
    db.save_user_meta(
        UserMeta(
            "u1",
            last_interaction_at=now - 10 * 60,
            last_sentiment=0.1,
            interaction_count=3,
        )
    )
    r = eng.check("u1", now=now)
    assert r.should_reach_out and r.trigger == "warm"
    assert r.message


def test_no_trigger_when_recent(engine):
    eng, db, _ = engine
    _seed_history(db)
    now = time.time()
    db.save_user_meta(UserMeta("u1", last_interaction_at=now - 60, last_sentiment=0.1))
    assert not eng.check("u1", now=now).should_reach_out


def test_emotion_trigger(engine):
    eng, db, s = engine
    _seed_history(db)
    now = time.time()
    db.save_user_meta(UserMeta("u1", last_interaction_at=now - s.proactive_emotion_min_idle_seconds - 60, last_sentiment=-0.6))
    r = eng.check("u1", now=now)
    assert r.should_reach_out and r.trigger == "emotion"


def test_insight_trigger_comfort(engine):
    eng, db, _ = engine
    _seed_history(db)
    now = time.time()
    db.add_message(
        Message(session_id="sess-u1", role="user", content="最近好累压力好大", created_at=now - 4000)
    )
    db.save_user_meta(
        UserMeta(
            "u1",
            last_interaction_at=now - 3600,
            last_sentiment=-0.5,
            sentiment_ema=-0.4,
            interaction_count=5,
        )
    )
    r = eng.check("u1", now=now)
    assert r.should_reach_out and r.trigger == "insight"
    assert r.insight is not None
    assert r.insight.proactive_need == "comfort"
    assert r.message


def test_insight_respects_cooldown(engine):
    eng, db, s = engine
    _seed_history(db)
    now = time.time()
    db.add_message(
        Message(session_id="sess-u1", role="user", content="好烦压力好大", created_at=now - 4000)
    )
    db.save_user_meta(
        UserMeta(
            "u1",
            last_interaction_at=now - 3600,
            last_sentiment=0.0,
            sentiment_ema=-0.4,
            last_proactive_at=now - 600,
        )
    )
    r = eng.check("u1", now=now)
    assert not r.should_reach_out or r.trigger != "insight"


def test_global_cooldown_blocks_warm(engine):
    eng, db, s = engine
    _seed_history(db)
    now = time.time()
    db.save_user_meta(
        UserMeta(
            "u1",
            last_interaction_at=now - 10 * 60,
            last_sentiment=0.1,
            interaction_count=3,
            last_proactive_at=now - 120,
        )
    )
    assert not eng.check("u1", now=now).should_reach_out


def test_insight_skipped_when_idle_too_short(engine):
    eng, db, s = engine
    _seed_history(db)
    now = time.time()
    db.add_message(
        Message(session_id="sess-u1", role="user", content="好烦", created_at=now - 100)
    )
    db.save_user_meta(
        UserMeta("u1", last_interaction_at=now - 200, last_sentiment=-0.5, sentiment_ema=-0.4)
    )
    r = eng.check("u1", now=now)
    assert not r.should_reach_out or r.trigger != "insight"


def test_event_trigger_has_priority(engine):
    eng, db, s = engine
    _seed_history(db)
    now = time.time()
    db.save_user_meta(UserMeta("u1", last_interaction_at=now - s.proactive_idle_seconds - 60, last_sentiment=-0.9))
    from app.domain import Event
    db.add_event(Event(user_id="u1", kind="interview", label="明天面试",
                        trigger_at=now, created_at=now))
    r = eng.check("u1", now=now)
    assert r.should_reach_out and r.trigger == "event"
    assert r.event_id is not None


def test_extract_events_relative_date():
    now = 1_000_000.0
    events = extract_events("我明天有个面试好紧张", now)
    assert len(events) == 1
    assert events[0].kind == "interview"
    assert events[0].trigger_at == pytest.approx(now + 86400)


def test_extract_events_none():
    assert extract_events("今天天气不错", 0.0) == []
