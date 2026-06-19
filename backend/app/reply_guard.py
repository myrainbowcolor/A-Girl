"""小模型/LLM 偶发「追问模板」时的轻量兜底（尊重用户边界）。"""
from __future__ import annotations

_CLOSED_MARKERS = (
    "不想说", "不想聊", "别问", "别烦", "没话说", "懒得说", "不说了", "随便", "算了",
)
_MINIMAL_UTTERANCES = {"..", "...", "…", "。", "嗯", "哦", "额"}
_PUSHY_REPLY_MARKERS = (
    "愿意多说", "你愿意多", "后来呢", "接着说", "有啥事", "可以帮忙", "多跟我说",
    "发生什么了", "想聊什么", "聊点什么", "聊点啥", "我们就聊", "有什么想聊",
    "喜欢做什么", "有什么爱好", "小确幸", "有什么好玩",
)


def user_is_closed(user_text: str) -> bool:
    t = user_text.strip()
    if not t or t in _MINIMAL_UTTERANCES or len(t) <= 2:
        return True
    return any(m in t for m in _CLOSED_MARKERS)


def reply_is_pushy(reply: str) -> bool:
    return any(m in reply for m in _PUSHY_REPLY_MARKERS)


def guard_closed_user_reply(user_text: str, reply: str) -> str:
    """用户封闭/极简时，若回复仍在追问，换成短句陪伴。"""
    if not user_is_closed(user_text) or not reply_is_pushy(reply):
        return reply
    if any(w in user_text for w in ("不想说", "不想聊", "别问", "别烦")):
        return "嗯，不说也行，我在这儿。你想说的时候再说~"
    return "嗯，我陪着。不急着说~"
