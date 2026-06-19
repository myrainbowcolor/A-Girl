"""小模型/LLM 偶发套话、复读时的轻量兜底（尊重用户边界）。"""
from __future__ import annotations

import hashlib
import re

_CLOSED_MARKERS = (
    "不想说", "不想聊", "别问", "别烦", "没话说", "懒得说", "不说了", "算了",
)
_MINIMAL_UTTERANCES = {"..", "...", "…", "。", "嗯", "哦", "额"}
_PUSHY_REPLY_MARKERS = (
    "愿意多说", "你愿意多", "后来呢", "接着说", "有啥事", "可以帮忙", "多跟我说",
    "发生什么了", "想聊什么", "聊点什么", "聊点啥", "聊啥", "我们就聊", "有什么想聊",
    "喜欢做什么", "有什么爱好", "小确幸", "有什么好玩", "你想聊", "分享一点",
)
_BAD_LLM_MARKERS = (
    "有相似之处", "温暖的少女", "我是你的陪伴者，而你", "共同的爱好",
    "让你知道我在这", "让你知道我在这世界", "暂时不聊了", "需要时间适应",
)
_META_PUSHBACK_MARKERS = ("为啥", "为什么", "何必", "一定要")
_IDENTITY_MARKERS = ("机器人", "人工智能", "是不是人", "真人吗", "AI", "ai")
_POSITIVE_MARKERS = ("真好", "谢谢", "感谢", "喜欢", "开心", "高兴", "温暖")

_META_PUSHBACK_REPLIES = (
    "不用一定要呀，想聊就聊，不想聊也完全可以。我在这儿，不催你~",
    "没有必须～你什么时候想开口都行，不想说我们就安静待着。",
    "不强迫的。你愿意来我在，不愿意也没事~",
)
_IDENTITY_REPLIES = (
    "对，我是 AI 陪伴角色小语，不是真人。但我会认真听你说话~",
    "嗯，我是小语，AI 陪伴角色。你不用把我当真人，当能说话的朋友就行~",
)
_CLOSED_REPLIES = (
    "嗯，不说也行，我在这儿。你想说的时候再说~",
    "好，不急着说。我陪着，你想开口了再说~",
)
_COMPANION_REPLIES = (
    "嗯，我陪着。不急着说~",
    "好，我在这儿。不急着开口~",
)
_POSITIVE_REPLIES = (
    "嘿嘿，你这么说我也挺开心的~",
    "听到你这么说，心里暖暖的。",
    "嘻嘻，能陪着你我也挺高兴的~",
)


def user_is_closed(user_text: str) -> bool:
    t = user_text.strip()
    if not t or t in _MINIMAL_UTTERANCES or len(t) <= 2:
        return True
    if t in {"随便", "算了"}:
        return True
    return any(m in t for m in _CLOSED_MARKERS)


def user_is_meta_pushback(user_text: str) -> bool:
    t = user_text.strip()
    return any(m in t for m in _META_PUSHBACK_MARKERS) and any(
        w in t for w in ("聊", "说话", "陪你", "跟你")
    )


def user_is_identity(user_text: str) -> bool:
    return any(m in user_text for m in _IDENTITY_MARKERS)


def user_is_positive(user_text: str) -> bool:
    return any(m in user_text for m in _POSITIVE_MARKERS)


def reply_is_pushy(reply: str) -> bool:
    return any(m in reply for m in _PUSHY_REPLY_MARKERS)


def reply_is_bad_llm(reply: str) -> bool:
    return any(m in reply for m in _BAD_LLM_MARKERS)


def _normalize_reply(text: str) -> str:
    t = re.sub(r"（[^）]*）", "", text)
    t = re.sub(r"^(嘿，|亲爱的，)", "", t)
    return t.strip()


def reply_similarity(a: str, b: str) -> float:
    na, nb = _normalize_reply(a), _normalize_reply(b)
    if not na or not nb:
        return 0.0
    if na == nb:
        return 1.0
    shorter, longer = (na, nb) if len(na) <= len(nb) else (nb, na)
    if shorter in longer and len(shorter) >= 10:
        return 0.92
    sa, sb = set(na), set(nb)
    union = sa | sb
    if not union:
        return 0.0
    return len(sa & sb) / len(union)


def _pick_variant(options: tuple[str, ...], seed: str) -> str:
    idx = int(hashlib.md5(seed.encode("utf-8")).hexdigest(), 16) % len(options)
    return options[idx]


def scene_fallback_reply(user_text: str, *, prior_reply: str = "") -> str | None:
    """关键场景下给出稳定、不追问的短回复。"""
    seed = user_text + prior_reply
    if user_is_identity(user_text):
        return _pick_variant(_IDENTITY_REPLIES, seed)
    if user_is_meta_pushback(user_text):
        return _pick_variant(_META_PUSHBACK_REPLIES, seed)
    if user_is_positive(user_text):
        return _pick_variant(_POSITIVE_REPLIES, seed)
    if user_is_closed(user_text):
        if any(w in user_text for w in ("不想说", "不想聊", "别问", "别烦")):
            return _pick_variant(_CLOSED_REPLIES, seed)
        return _pick_variant(_COMPANION_REPLIES, seed)
    return None


def guard_closed_user_reply(user_text: str, reply: str) -> str:
    """用户封闭/极简时，若回复仍在追问，换成短句陪伴。"""
    if not user_is_closed(user_text) or not reply_is_pushy(reply):
        return reply
    fb = scene_fallback_reply(user_text)
    return fb or "嗯，我陪着。不急着说~"


def meta_pushback_ok(reply: str) -> bool:
    return any(w in reply for w in ("不用", "不强迫", "没有必须", "不催", "不想聊也", "不必须"))


def _identity_answered(reply: str) -> bool:
    return any(w in reply for w in ("AI", "小语", "人工智能", "陪伴角色"))


def reply_is_companion_only(reply: str) -> bool:
    r = _normalize_reply(reply)
    return any(p in r for p in ("不急着说", "不说也行", "我陪着。不"))


def reply_is_companion_ok(reply: str) -> bool:
    r = _normalize_reply(reply)
    if reply_is_pushy(r):
        return False
    if len(r) > 48:
        return False
    return any(w in r for w in ("陪着", "不急着", "不说也行", "没关系", "不想说也", "嗯，好", "嗯，我"))


def polish_reply(user_text: str, reply: str, *, prior_reply: str = "") -> str:
    """统一兜底：坏套话、复读、场景不匹配时替换为短句。"""
    reply = guard_closed_user_reply(user_text, reply)

    needs_fallback = (
        reply_is_bad_llm(reply)
        or (user_is_meta_pushback(user_text) and (reply_is_pushy(reply) or not meta_pushback_ok(reply)))
        or (user_is_identity(user_text) and (reply_is_bad_llm(reply) or not _identity_answered(reply)))
        or (user_is_positive(user_text) and reply_is_companion_only(reply))
        or (user_is_closed(user_text) and not reply_is_companion_ok(reply))
    )
    if needs_fallback:
        fb = scene_fallback_reply(user_text, prior_reply=prior_reply)
        if fb:
            return fb

    if prior_reply and reply_similarity(reply, prior_reply) >= 0.82:
        fb = scene_fallback_reply(user_text, prior_reply=prior_reply + reply)
        if fb and reply_similarity(fb, prior_reply) < 0.82:
            return fb
        if user_is_positive(user_text):
            return _pick_variant(_POSITIVE_REPLIES, prior_reply + user_text)
        if user_is_closed(user_text):
            return _pick_variant(_COMPANION_REPLIES, prior_reply + user_text + reply)

    return reply


def prior_assistant_reply(history: list[dict[str, str]]) -> str:
    for m in reversed(history):
        if m.get("role") == "assistant":
            return m.get("content", "")
    return ""
