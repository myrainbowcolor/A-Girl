"""小模型/LLM 偶发套话、复读时的轻量兜底（尊重用户边界）。"""
from __future__ import annotations

import hashlib
import re

_CLOSED_MARKERS = (
    "不想说", "不想聊", "别问", "别烦", "没话说", "懒得说", "不说了", "算了",
    "不想说话", "不是很想说话", "不太想说话",
)
_MINIMAL_UTTERANCES = {"..", "...", "…", "。", "嗯", "哦", "额", "好", "行"}
_GREETING_SHORT = {"你好", "嗨", "哈喽", "在吗", "早上好", "晚上好", "午安"}
# 整句极简 masking/回避口语：需轻柔共情，非封闭边界（与 emotion.analyzer 对齐）
_MINIMAL_MASKING = frozenset({"还好", "还行", "一般"})
_MINIMAL_EVASIVE = frozenset({"不知道", "说不清", "说不上"})
_MINIMAL_FATIGUE = frozenset({"累"})
_PUSHY_REPLY_MARKERS = (
    "愿意多说", "你愿意多", "后来呢", "然后呢", "接着说", "有啥事", "可以帮忙", "多跟我说",
    "发生什么了", "想聊什么", "聊点什么", "聊点啥", "聊啥", "我们就聊", "有什么想聊",
    "喜欢做什么", "有什么爱好", "小确幸", "有什么好玩", "你想聊", "分享一点",
    "我懂。然后呢", "后来怎么样了",
)
_BAD_LLM_MARKERS = (
    "有相似之处", "温暖的少女", "我是你的陪伴者，而你", "共同的爱好",
    "让你知道我在这", "让你知道我在这世界", "暂时不聊了", "需要时间适应",
)
_GENERIC_LLM_MARKERS = (
    "有什么新鲜事", "咱们聊聊天吧", "我理解了", "我明白了", "我听说你们",
)
_FILLER_HEAD_RE = re.compile(r"^(（[^）]*）)?(嗯+[…\.~]?|呃+)+[，,]?")
_GENERIC_MOCK_MARKERS = (
    "愿意多说一点吗", "后来呢，发生什么了", "嗯，我在听呢——后来呢",
    "你再多跟我说说", "嗯嗯，然后呢", "我在听呢", "接着说，我听着",
    "你继续说", "我懂。然后呢", "接着说，我听着呢",
    "嘿，后来怎么样了", "你再多跟我说说呗",
    "我听到了。是最近", "一直压着你", "从哪儿说起都行", "先吐槽还是先理理",
    "今天这事你想先聊哪一块",
)
_META_PUSHBACK_MARKERS = ("为啥", "为什么", "何必", "一定要")
_IDENTITY_MARKERS = ("机器人", "人工智能", "是不是人", "真人吗", "AI", "ai")

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
_APOLOGY_REPLIES = (
    "抱歉刚才太敷衍了。我认真听，你慢慢说~",
    "对不起，我不该一直嗯嗯的。你想聊什么，我好好回应~",
)


def user_is_closed(user_text: str) -> bool:
    t = user_text.strip()
    if t in _MINIMAL_MASKING or t in _MINIMAL_EVASIVE or t in _MINIMAL_FATIGUE:
        return False
    if not t:
        return True
    if t in _GREETING_SHORT or re.fullmatch(r"(?i)hi|hello", t):
        return False
    if t in _MINIMAL_UTTERANCES or len(t) <= 2:
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
    return any(m in user_text for m in _IDENTITY_MARKERS) or any(
        w in user_text for w in ("怎么称呼", "称呼你", "叫什么")
    )


def user_complains_filler(user_text: str) -> bool:
    return any(w in user_text for w in ("别嗯", "不要嗯", "嗯嗯", "敷衍", "太敷衍"))


def reply_is_filler_heavy(reply: str) -> bool:
    r = _normalize_reply(reply)
    if _FILLER_HEAD_RE.match(reply.strip()):
        return True
    if r.count("嗯") >= 2 and len(r) <= 64:
        return True
    return bool(re.search(r"(嗯+[…\.~]?){2,}", r))


def reply_is_generic_llm(reply: str) -> bool:
    r = _normalize_reply(reply)
    if any(m in r for m in _GENERIC_LLM_MARKERS) and len(r) <= 56:
        return True
    return r.startswith("嗯") and reply_is_pushy(r)


def reply_is_pushy(reply: str) -> bool:
    return any(m in reply for m in _PUSHY_REPLY_MARKERS)


def reply_is_bad_llm(reply: str) -> bool:
    return any(m in reply for m in _BAD_LLM_MARKERS)


def reply_is_generic_scene(reply: str) -> bool:
    """场景引擎未命中具体分支时的问卷式兜底，不宜直接采用。"""
    return any(m in reply for m in _GENERIC_MOCK_MARKERS)


reply_is_generic_mock = reply_is_generic_scene  # 兼容旧名


def reply_is_self_talk(reply: str) -> bool:
    """小模型把 NPC 写成在聊自己工作/生活。"""
    return any(w in reply for w in ("我最近", "我的工作", "最近工作", "最近忙吗"))


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


def needs_mock_fallback(reply: str, user_text: str, *, prior_reply: str = "") -> bool:
    """LLM 输出明显不可用，应回退到场景引擎（mock 的场景逻辑）。"""
    from .out_of_world_guard import (
        reply_is_stiff_deflection,
        reply_looks_factual_encyclopedia,
        reply_uses_real_world_cognition,
        user_asks_out_of_world,
    )

    if (
        user_asks_out_of_world(user_text)
        or reply_looks_factual_encyclopedia(reply)
        or reply_uses_real_world_cognition(reply, user_text)
    ):
        return True
    if reply_is_stiff_deflection(reply):
        return True
    if reply_is_bad_llm(reply) or reply_is_self_talk(reply):
        return True
    if reply_is_filler_heavy(reply) or reply_is_generic_llm(reply) or reply_is_generic_scene(reply):
        return True
    if user_complains_filler(user_text):
        return True
    if prior_reply and reply_similarity(reply, prior_reply) >= 0.88:
        return True
    if user_is_closed(user_text) and reply_is_pushy(reply):
        return True
    if user_is_meta_pushback(user_text) and reply_is_pushy(reply):
        return True
    if reply_is_pushy(reply) and user_wants_wrap_up(user_text):
        return True
    return False


def user_wants_wrap_up(user_text: str) -> bool:
    """用户表示话题结束，不应再追问「后来呢」类套话。"""
    t = user_text.strip()
    return t in ("后来呢", "然后呢", "接着呢", "还有呢") or any(
        w in t for w in ("没啥了", "就这些", "没别的", "没有了", "不说了")
    )

def _pick_variant(options: tuple[str, ...], seed: str) -> str:
    idx = int(hashlib.md5(seed.encode("utf-8")).hexdigest(), 16) % len(options)
    return options[idx]


def scene_fallback_reply(user_text: str, *, prior_reply: str = "") -> str | None:
    """仅在最坏情况下使用的极短兜底（优先用 mock 场景引擎）。"""
    from .out_of_world_guard import user_asks_out_of_world

    seed = user_text + prior_reply
    if user_asks_out_of_world(user_text):
        from .out_of_world_guard import compose_out_of_world_reply

        return compose_out_of_world_reply(user_text, seed=seed)
    if user_is_identity(user_text):
        return _pick_variant(_IDENTITY_REPLIES, seed)
    if user_complains_filler(user_text):
        return _pick_variant(_APOLOGY_REPLIES, seed)
    if user_is_meta_pushback(user_text):
        return _pick_variant(_META_PUSHBACK_REPLIES, seed)
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


def _compose_or_fallback(
    user_text: str,
    *,
    prior_reply: str = "",
    history: list[dict[str, str]] | None = None,
) -> str | None:
    from .dialogue_compose import compose_contextual_reply

    composed = compose_contextual_reply(
        user_text, history or [], prior_reply=prior_reply
    )
    if composed:
        return composed
    return scene_fallback_reply(user_text, prior_reply=prior_reply)


def polish_reply(
    user_text: str,
    reply: str,
    *,
    prior_reply: str = "",
    history: list[dict[str, str]] | None = None,
) -> str:
    """轻量后处理：只修追问/复读/坏套话，保留 LLM 或场景引擎的自然回复。"""
    reply = guard_closed_user_reply(user_text, reply)

    from .out_of_world_guard import (
        reply_is_stiff_deflection,
        reply_looks_factual_encyclopedia,
        reply_uses_real_world_cognition,
        user_asks_out_of_world,
    )

    if (
        user_asks_out_of_world(user_text)
        or reply_looks_factual_encyclopedia(reply)
        or reply_uses_real_world_cognition(reply, user_text)
        or reply_is_stiff_deflection(reply)
        or reply_is_bad_llm(reply)
        or reply_is_filler_heavy(reply)
        or reply_is_generic_llm(reply)
        or reply_is_generic_scene(reply)
        or user_complains_filler(user_text)
        or (reply_is_pushy(reply) and user_wants_wrap_up(user_text))
    ):
        alt = _compose_or_fallback(user_text, prior_reply=prior_reply, history=history)
        if alt:
            return alt
        cleaned = _FILLER_HEAD_RE.sub("", reply).strip()
        if cleaned and not reply_is_filler_heavy(cleaned):
            reply = cleaned

    if prior_reply and reply_similarity(reply, prior_reply) >= 0.88:
        alt = _compose_or_fallback(
            user_text, prior_reply=prior_reply + reply, history=history
        )
        if alt and reply_similarity(alt, prior_reply) < 0.88:
            return alt

    return ensure_reply_diversity(
        reply, user_text, history or [], prior_reply=prior_reply
    )


def prior_assistant_reply(history: list[dict[str, str]]) -> str:
    for m in reversed(history):
        if m.get("role") == "assistant":
            return m.get("content", "")
    return ""


def recent_assistant_replies(
    history: list[dict[str, str]], limit: int = 6
) -> list[str]:
    out: list[str] = []
    for m in reversed(history):
        if m.get("role") == "assistant":
            text = (m.get("content") or "").strip()
            if text:
                out.append(text)
            if len(out) >= limit:
                break
    return out


def reply_repeats_history(
    reply: str,
    history: list[dict[str, str]] | list[str],
    *,
    threshold: float = 0.82,
) -> bool:
    """是否与近期 assistant 回复高度相似（会话级防复读）。"""
    if isinstance(history, list) and history and isinstance(history[0], str):
        recent = history
    else:
        recent = recent_assistant_replies(history)  # type: ignore[arg-type]
    return any(reply_similarity(reply, prev) >= threshold for prev in recent)


_DIVERSITY_REPLIES = (
    "嗯，我在呢。你先随便丢几个词给我也行~",
    "好，我收到了。不用一次说完~",
    "我听着。哪一块你现在最想提？",
    "嗯，这事不急。你想从哪儿开始说？",
    "好，我接住了。慢慢讲~",
    "我在。你想到什么就说什么~",
    "嗯，不用整理成完整句子。我听得懂~",
    "好，先歇口气再说也行~",
)


def ensure_reply_diversity(
    reply: str,
    user_text: str,
    history: list[dict[str, str]],
    *,
    prior_reply: str = "",
) -> str:
    """根治复读：与近几轮 assistant 回复撞车则强制换句。"""
    recent = recent_assistant_replies(history)
    if not reply_repeats_history(reply, recent):
        return reply

    from .dialogue_compose import compose_open_reply

    alt = compose_open_reply(
        user_text,
        history,
        prior_reply=prior_reply,
        avoid=recent + [reply],
    )
    if alt and not reply_repeats_history(alt, recent):
        return alt

    seed_base = user_text + prior_reply + "".join(recent[:2])
    for i in range(len(_DIVERSITY_REPLIES) * 2):
        alt = _pick_variant(_DIVERSITY_REPLIES, seed_base + f"#{i}")
        if not reply_repeats_history(alt, recent):
            return alt
    return reply
