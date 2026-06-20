"""开放话题的上下文拼装（scene_first 第二层，无 LLM）。"""
from __future__ import annotations

import hashlib
import re


def _pick(options: tuple[str, ...], seed: str) -> str:
    idx = int(hashlib.md5(seed.encode("utf-8")).hexdigest(), 16) % len(options)
    return options[idx]


def _user_history(history: list[dict[str, str]]) -> str:
    return " ".join(m.get("content", "") for m in history if m.get("role") == "user")


def _last_user(history: list[dict[str, str]]) -> str:
    for m in reversed(history):
        if m.get("role") == "user":
            return m.get("content", "")
    return ""


def compose_contextual_reply(user_text: str, history: list[dict[str, str]]) -> str | None:
    """根据本轮 + 近期用户话拼装自然回复；未覆盖返回 None。"""
    text = user_text.strip()
    prior_users = _user_history(history)
    seed = text + prior_users[-80:]

    if any(w in text for w in ("随便聊聊", "随便聊", "闲聊一下", "闲聊")):
        return _pick(
            (
                "好呀～今天过得怎么样，有没有一件小事想跟我分享？",
                "行，咱慢慢聊。你现在是放松下来了，还是心里还绷着？",
                "嗯，我在这儿。你想从今天的事聊起，还是就随便发发呆也行~",
            ),
            seed,
        )

    if any(w in text for w in ("空空的", "空落", "心里空", "没原因", "没啥具体", "也没啥")):
        return _pick(
            (
                "空落落的时候不一定非得有事才行。我陪着，你想说就说~",
                "嗯，这种没来由的空我也懂。不用逼自己找原因，先歇一会儿？",
                "没具体的事也会难受的。我在这儿，不急着把你问明白~",
            ),
            seed,
        )

    if text in ("还行", "还行吧", "一般", "还好吧") or re.fullmatch(r"还?行吧?", text):
        return _pick(
            (
                "还行呀……是今天平平淡淡，还是其实有点什么事憋着？",
                "嗯，听起来不糟也不特别开心？要是愿意，可以跟我多聊一句~",
            ),
            seed,
        )

    if any(w in text for w in ("哈哈哈", "哈哈", "嘿嘿")):
        return _pick(
            (
                "哈哈，听你笑我也跟着轻松点了～发生什么好事啦？",
                "嘻嘻，今天心情不错呀？",
            ),
            seed,
        )

    if "怎么办" in text or "咋办" in text:
        ctx = prior_users + text
        if any(w in ctx for w in ("猫", "狗", "宠物", "橘子", "打翻", "杯子")):
            return _pick(
                (
                    "先别跟它置气啦～把易碎的东西收一收，等它消停一会儿再理它？",
                    "捣蛋完有时会怂怂的哈哈。你先看看它躲哪了，别急着骂~",
                ),
                seed,
            )
        if any(w in ctx for w in ("老板", "加班", "工作", "辞职")):
            return (
                "工作上的事先别急着做决定。今晚把自己从情绪里捞出来，"
                "明天清醒了再想想下一步？"
            )

    if "辞职信" in text or ("帮我写" in text and "信" in text):
        return (
            "正式文书我帮你写不合适～但你要是想聊聊为什么想走、"
            "最委屈的是哪一块，我可以认真听。"
        )

    if text in ("?", "？", "…", "..", "...") or len(text) <= 1:
        return "我在这儿呢。不急着说，你想开口了再说~"

    if any(w in text for w in ("hello", "hi", "HI", "Hello")) and len(text) <= 12:
        return "嗨～我是小语。今天想聊点什么？"

    if any(w in text for w in ("不愿意", "不想聊", "别说了")):
        return "好，不聊也行。我陪着，你想说的时候再说~"

    # 承接上一轮：用户纠正「请教你/什么意思」
    if any(w in text for w in ("请教你", "什么意思", "你在说啥", "没听懂")):
        topic = _last_user(history)
        if any(w in topic for w in ("女朋友", "男朋友", "对象", "拉近")):
            return (
                "抱歉刚才没说明白。我是想问你：你们最近见面多吗？"
                "有没有一件你想主动做的小事？"
            )
        return "抱歉，我刚才没接准。你再说具体一点，我认真帮你理~"

    return None
