"""主动推送通道：把主动关心消息实时投递给客户端。

两种通道：
- SSE（Server-Sent Events）：独立 Web / 长连接客户端实时收主动消息；
- Webhook：嵌入游戏 / 后端服务，主动消息 POST 到配置的回调地址（可由游戏转成 NPC 气泡）。

进程内 pub/sub，单实例足够（研究型单玩家）；生产期可换 Redis pub/sub + 消息队列。
"""
from __future__ import annotations

import json
import queue
import threading
import urllib.request

from .config import Settings


class PushHub:
    def __init__(self, settings: Settings) -> None:
        self._s = settings
        self._subscribers: dict[str, list[queue.Queue]] = {}
        self._lock = threading.Lock()

    # ---------- SSE 订阅 ----------
    def subscribe(self, user_id: str) -> queue.Queue:
        q: queue.Queue = queue.Queue(maxsize=100)
        with self._lock:
            self._subscribers.setdefault(user_id, []).append(q)
        return q

    def unsubscribe(self, user_id: str, q: queue.Queue) -> None:
        with self._lock:
            subs = self._subscribers.get(user_id, [])
            if q in subs:
                subs.remove(q)

    def subscriber_count(self, user_id: str) -> int:
        with self._lock:
            return len(self._subscribers.get(user_id, []))

    # ---------- 投递 ----------
    def publish(self, user_id: str, payload: dict) -> dict:
        """把一条主动消息推给该用户的所有 SSE 订阅者，并触发 webhook（若配置）。

        返回投递统计，便于测试与观测。
        """
        delivered = 0
        with self._lock:
            for q in list(self._subscribers.get(user_id, [])):
                try:
                    q.put_nowait(payload)
                    delivered += 1
                except queue.Full:
                    pass
        webhook_ok = self._fire_webhook(user_id, payload)
        return {"sse_delivered": delivered, "webhook": webhook_ok}

    def _fire_webhook(self, user_id: str, payload: dict) -> str:
        url = self._s.push_webhook_url
        if not url:
            return "disabled"
        try:
            body = json.dumps({"user_id": user_id, **payload}).encode("utf-8")
            req = urllib.request.Request(
                url, data=body, headers={"Content-Type": "application/json"}, method="POST"
            )
            with urllib.request.urlopen(req, timeout=5) as resp:
                return f"ok:{resp.status}"
        except Exception as e:  # webhook 失败不应影响主流程
            return f"error:{type(e).__name__}"
