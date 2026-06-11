from app.config import Settings
from app.push import PushHub


def test_subscribe_and_publish():
    hub = PushHub(Settings(push_webhook_url=""))
    q = hub.subscribe("u1")
    stats = hub.publish("u1", {"message": "hi"})
    assert stats["sse_delivered"] == 1
    assert stats["webhook"] == "disabled"
    assert q.get_nowait()["message"] == "hi"


def test_publish_no_subscribers():
    hub = PushHub(Settings(push_webhook_url=""))
    stats = hub.publish("nobody", {"message": "x"})
    assert stats["sse_delivered"] == 0


def test_unsubscribe():
    hub = PushHub(Settings(push_webhook_url=""))
    q = hub.subscribe("u1")
    assert hub.subscriber_count("u1") == 1
    hub.unsubscribe("u1", q)
    assert hub.subscriber_count("u1") == 0


def test_multiple_subscribers_all_receive():
    hub = PushHub(Settings(push_webhook_url=""))
    q1, q2 = hub.subscribe("u1"), hub.subscribe("u1")
    stats = hub.publish("u1", {"message": "broadcast"})
    assert stats["sse_delivered"] == 2
    assert q1.get_nowait()["message"] == "broadcast"
    assert q2.get_nowait()["message"] == "broadcast"
