import tempfile
import time

import pytest

from app.config import Settings
from app.db import Database
from app.domain import Persona, UserMeta
from app.proactivity import ProactivityEngine, extract_events


@pytest.fixture
def engine():
    with tempfile.NamedTemporaryFile(suffix=".db") as f:
        db = Database(f.name)
        s = Settings(db_path=f.name, proactive_idle_seconds=6 * 3600)
        yield ProactivityEngine(db, s, Persona()), db, s
        db.close()


def test_no_trigger_without_meta(engine):
    eng, _, _ = engine
    assert not eng.check("u1").should_reach_out


def test_idle_trigger(engine):
    eng, db, s = engine
    now = time.time()
    db.save_user_meta(UserMeta("u1", last_interaction_at=now - 10 * 3600, last_sentiment=0.1))
    r = eng.check("u1", now=now)
    assert r.should_reach_out and r.trigger == "idle"
    assert r.message


def test_no_trigger_when_recent(engine):
    eng, db, _ = engine
    now = time.time()
    db.save_user_meta(UserMeta("u1", last_interaction_at=now - 60, last_sentiment=0.1))
    assert not eng.check("u1", now=now).should_reach_out


def test_emotion_trigger(engine):
    eng, db, _ = engine
    now = time.time()
    db.save_user_meta(UserMeta("u1", last_interaction_at=now - 3600, last_sentiment=-0.6))
    r = eng.check("u1", now=now)
    assert r.should_reach_out and r.trigger == "emotion"


def test_event_trigger_has_priority(engine):
    eng, db, _ = engine
    now = time.time()
    db.save_user_meta(UserMeta("u1", last_interaction_at=now - 10 * 3600, last_sentiment=-0.9))
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
