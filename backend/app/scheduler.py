"""主动关心后台调度器（轻量、无外部依赖）。

启用后（AGIRL_PROACTIVE_SCHEDULER_ENABLED=true），后台线程周期性遍历已知用户，
评估主动关心触发器，把命中的主动消息投递到内存收件箱（outbox）。
独立 Web 前端或嵌入游戏可轮询 /api/proactive/outbox/{user_id} 取走。

研究型单用户场景足够；生产期可替换为 APScheduler/Celery + 真实推送通道（IM/推送）。
"""
from __future__ import annotations

import threading
import time

from .config import Settings
from .db import Database
from .push import PushHub


class ProactiveScheduler:
    def __init__(self, db: Database, orchestrator, settings: Settings, push: PushHub | None = None) -> None:
        self._db = db
        self._orch = orchestrator
        self._s = settings
        self._push = push
        self._outbox: dict[str, list[dict]] = {}
        self._lock = threading.Lock()
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None

    def start(self) -> None:
        if not self._s.proactive_scheduler_enabled:
            return
        if self._thread and self._thread.is_alive():
            return
        self._stop.clear()
        self._thread = threading.Thread(target=self._loop, name="proactive-scheduler", daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()

    def _loop(self) -> None:
        while not self._stop.wait(self._s.proactive_scheduler_interval_seconds):
            try:
                self._tick()
            except Exception:  # 调度器不应因单次异常而崩溃
                pass

    def _tick(self) -> None:
        for user_id in self._db.all_user_ids():
            result, avatar = self._orch.deliver_proactive(user_id)
            if result.should_reach_out:
                item = {
                    "type": "proactive",
                    "trigger": result.trigger,
                    "reason": result.reason,
                    "message": result.message,
                    "avatar": {
                        "expression": avatar.expression,
                        "intensity": avatar.intensity,
                        "animation": avatar.animation,
                    } if avatar else None,
                    "ts": time.time(),
                }
                self._enqueue(user_id, item)
                if self._push is not None:
                    self._push.publish(user_id, item)

    def _enqueue(self, user_id: str, item: dict) -> None:
        with self._lock:
            self._outbox.setdefault(user_id, []).append(item)

    def drain(self, user_id: str) -> list[dict]:
        with self._lock:
            items = self._outbox.get(user_id, [])
            self._outbox[user_id] = []
            return items
