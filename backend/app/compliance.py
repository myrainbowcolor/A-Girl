"""未成年人合规：年龄确认门 + 家长可见安全审计日志。

- 年龄确认：用户首次使用需确认年龄，记录在 user_consent 表；未确认前拒绝对话。
- 安全审计日志：把危机/成人/暴力/隐私等安全事件追加写入审计日志文件，
  家长/监护人可查看，便于干预。审计同时落 DB 供 API 查询。

研究阶段为轻量实现；生产期应结合可信年龄核验、家长账户绑定与合规留存策略。
"""
from __future__ import annotations

import json
import threading
import time

from .db import Database


class AuditLogger:
    def __init__(self, db: Database, log_path: str) -> None:
        self._db = db
        self._log_path = log_path
        self._lock = threading.Lock()

    def log_safety_event(self, user_id: str, category: str, user_text: str) -> None:
        ts = time.time()
        record = {
            "ts": ts,
            "user_id": user_id,
            "category": category,
            "excerpt": user_text[:80],
        }
        # 落 DB（供家长安全日志 API 查询）
        self._db.add_audit_event(user_id, category, user_text[:200], ts)
        # 追加写入文件（家长可见的安全日志）
        try:
            with self._lock:
                with open(self._log_path, "a", encoding="utf-8") as f:
                    f.write(json.dumps(record, ensure_ascii=False) + "\n")
        except OSError:
            pass  # 文件写入失败不影响主流程


class AgeGate:
    """年龄确认门。"""

    def __init__(self, db: Database, require: bool, min_age: int) -> None:
        self._db = db
        self._require = require
        self._min_age = min_age

    def has_consent(self, user_id: str) -> bool:
        if not self._require:
            return True
        return self._db.get_consent(user_id) is not None

    def record_consent(self, user_id: str, age: int) -> dict:
        """记录年龄确认。返回 {"ok": bool, "reason": str|None}。"""
        if self._min_age and age < self._min_age:
            return {"ok": False, "reason": f"需年满 {self._min_age} 岁"}
        self._db.save_consent(user_id, age, time.time())
        return {"ok": True, "reason": None}

    @property
    def required(self) -> bool:
        return self._require
