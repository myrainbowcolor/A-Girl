import tempfile

import pytest

from app.compliance import AgeGate, AuditLogger
from app.db import Database


@pytest.fixture
def db():
    with tempfile.NamedTemporaryFile(suffix=".db") as f:
        d = Database(f.name)
        yield d
        d.close()


def test_age_gate_blocks_until_consent(db):
    gate = AgeGate(db, require=True, min_age=0)
    assert not gate.has_consent("u1")
    gate.record_consent("u1", 15)
    assert gate.has_consent("u1")


def test_age_gate_disabled_allows_all(db):
    gate = AgeGate(db, require=False, min_age=0)
    assert gate.has_consent("anyone")


def test_min_age_rejection(db):
    gate = AgeGate(db, require=True, min_age=13)
    res = gate.record_consent("u1", 10)
    assert not res["ok"] and "13" in res["reason"]
    assert not gate.has_consent("u1")
    ok = gate.record_consent("u1", 16)
    assert ok["ok"] and gate.has_consent("u1")


def test_audit_logger_persists(db):
    with tempfile.NamedTemporaryFile(suffix=".log") as lf:
        logger = AuditLogger(db, lf.name)
        logger.log_safety_event("u1", "crisis", "我不想活了")
        logger.log_safety_event("u1", "adult", "做我女朋友")
        events = db.audit_events("u1")
        assert len(events) == 2
        cats = {e["category"] for e in events}
        assert cats == {"crisis", "adult"}
        # 文件也应写入
        with open(lf.name, encoding="utf-8") as fh:
            lines = [l for l in fh.read().splitlines() if l.strip()]
        assert len(lines) == 2
