"""开放话题的上下文拼装（scene_first 第二层，无 LLM）。"""
from __future__ import annotations

import hashlib
import re

from .llm.mock import _pet_name_from_context
from .out_of_world_guard import compose_out_of_world_reply, user_asks_out_of_world
from .sentiment_lexicon import contains_keyword, has_casual_social_context, user_complains_bot_reply

_MORNING_GREETING_MARKERS = ("早呀", "早安", "早上好", "早啊")
_COMMUTE_MARKERS = ("又要上班", "不想起床", "困死")
_WORK_VENT_MARKERS = ("累", "烦", "加班", "好烦", "好晚", "十点", "九点", "心累", "烦死", "熬")


def _is_morning_greeting(text: str) -> bool:
    """早安/通勤寒暄（非工作压力倾诉）。"""
    t = text.strip()
    if any(v in t for v in _WORK_VENT_MARKERS):
        return False
    if any(m in t for m in _MORNING_GREETING_MARKERS):
        return True
    return any(m in t for m in _COMMUTE_MARKERS)


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


def _last_assistant(history: list[dict[str, str]]) -> str:
    for m in reversed(history):
        if m.get("role") == "assistant":
            return m.get("content", "")
    return ""


def _too_similar(candidate: str, avoid: list[str], threshold: float = 0.82) -> bool:
    from .reply_guard import reply_similarity

    return any(reply_similarity(candidate, prev) >= threshold for prev in avoid if prev)


def compose_open_reply(
    user_text: str,
    history: list[dict[str, str]],
    *,
    prior_reply: str = "",
    avoid: list[str] | None = None,
) -> str:
    """开放话题兜底：根据近期上下文生成不重复接话（scene/compose 均未命中时）。"""
    avoid = list(avoid or [])
    text = user_text.strip()
    prior_users = _user_history(history)
    prior_assistant = prior_reply or _last_assistant(history)
    repeat_n = sum(1 for m in history if m.get("role") == "user" and m.get("content") == text)
    seed_base = text + prior_users[-100:] + prior_assistant[-40:] + f"#{repeat_n}"

    topic = ""
    for line in reversed([m.get("content", "") for m in history if m.get("role") == "user"]):
        t = line.strip()
        if len(t) >= 3 and t not in ("嗯", "哦", "好", "行", "还行", "还好"):
            topic = t[:14] + ("…" if len(t) > 14 else "")
            break

    pool: list[str] = []
    ctx = prior_users + text
    if any(w in ctx for w in ("烦", "累", "难过", "委屈", "压力", "焦虑", "心累")):
        pool.extend(
            [
                "听起来你心里挺沉的。是突然这样，还是已经有一阵子了？",
                "嗯，这种时候先别逼自己想明白。我陪着，你想从哪一句开始？",
                "我收到了。今天最耗你的是哪一块？",
            ]
        )
    if any(w in ctx for w in ("工作", "上班", "公司", "老板", "加班")):
        pool.extend(
            [
                "工作的事啊……是事情堆太多，还是某一件特别委屈？",
                "嗯，上班确实容易把人掏空。你想先吐槽还是先理理？",
                "我听着。是最近都这样，还是就今天特别难？",
            ]
        )
    if topic:
        pool.append(f"嗯，{topic} 这事你想先聊哪一块？")
    pool.extend(
        [
            "嗯，我在呢。你先随便丢几个词给我也行~",
            "好，我收到了。不用一次说完~",
            "我听着。哪一块你现在最想提？",
            "嗯，这事不急。你想从哪儿开始说？",
            "好，我接住了。慢慢讲~",
            "我在。你想到什么就说什么~",
        ]
    )

    for i in range(max(len(pool) * 3, 12)):
        candidate = _pick(tuple(pool), seed_base + f"@{i}")
        if not _too_similar(candidate, avoid):
            return candidate
    return pool[0]


def compose_contextual_reply(
    user_text: str,
    history: list[dict[str, str]],
    *,
    prior_reply: str = "",
) -> str | None:
    """根据本轮 + 近期用户话拼装自然回复；未覆盖返回 None。"""
    text = user_text.strip()
    prior_users = _user_history(history)
    prior_assistant = prior_reply or _last_assistant(history)
    repeat_n = sum(1 for m in history if m.get("role") == "user" and m.get("content") == text)
    seed = text + prior_users[-80:] + prior_assistant[-40:] + f"#{repeat_n}"

    if user_asks_out_of_world(text):
        return compose_out_of_world_reply(text, seed=seed)

    if user_complains_bot_reply(text):
        return _pick(
            (
                "对不起，刚才确实是我没接对。你现在不开心的感受我听见了，我先陪着你。",
                "你说得对，我应该先安慰你。抱歉刚才跑偏了——此刻你最难受的是哪一块？",
                "嗯，是我刚才没接住。先别管回忆那些事了，我在这儿，你想怎么说都行。",
            ),
            seed,
        )

    if contains_keyword(text, "不开心") or text in ("我不开心", "我不高兴了"):
        return _pick(
            (
                "嗯……不开心的感觉我收到了。我先陪着你，不急着讲道理。",
                "听起来你现在心里挺沉的。我在呢，你想从哪一句开始说都行。",
                "我听见你不开心了。先缓口气，我哪儿也不去。",
            ),
            seed,
        )

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

    if text in ("还行", "还行吧", "一般", "还好吧", "还好") or re.fullmatch(r"还?行吧?", text):
        return _pick(
            (
                "还行呀……是今天平平淡淡，还是其实有点什么事憋着？",
                "听着不糟也不特别开心？要是愿意，可以跟我多聊一句~",
            ),
            seed,
        )

    if text == "累":
        return _pick(
            (
                "累呀……先别硬撑，缓口气。是身子累还是心里也一起累了？",
                "听着就心疼，累的时候能说出来已经很好了。先歇一会儿，我陪着~",
            ),
            seed,
        )

    # 倚靠倾诉（须在通用负面兜底之前，与 mock.py 场景分支对齐）
    if any(w in text for w in ("靠着", "想靠着", "倚靠")):
        is_intimate = any(m in prior_assistant for m in ("亲爱的", "宝贝", "抱抱"))
        if is_intimate or "靠着你说" in text:
            return _pick(
                (
                    "过来，靠着我慢慢说。今天辛苦了，我哪儿也不去。",
                    "嗯，靠过来吧。累的时候不用硬撑，想说什么就说~",
                ),
                seed,
            )
        return _pick(
            (
                "累的时候跟我说就好，我陪着。今天最耗你的是哪一块儿？",
                "嗯，我在呢。不想整理成完整句子也行，慢慢说~",
            ),
            seed,
        )

    # 宠物捣蛋续聊（须在通用「哈哈」报喜之前，与 mock.py 场景分支对齐）
    pet_name = _pet_name_from_context(prior_users + " " + text, "")
    if (
        pet_name is not None
        and "它" in text
        and any(w in text for w in ("打翻", "杯子", "搞破坏", "淘气", "拆家"))
    ):
        refer = pet_name if pet_name else "小家伙"
        if "打翻" in text or "杯子" in text:
            return _pick(
                (
                    f"哈哈，{refer}又把杯子打翻啦？这种捣蛋精真是又气又好笑～它现在躲起来了吗？",
                    f"哈哈，{refer}搞破坏啦？易碎的东西可得收一收～它这会儿怂了没？",
                ),
                seed,
            )
        return _pick(
            (
                f"哈哈，{refer}又淘气了～今天怎么这么有精神呀？",
                f"捣蛋完有时会怂怂的哈哈，{refer}这会儿干嘛呢？",
            ),
            seed,
        )

    # 想念 / 好久未见（须在「哈哈」报喜之前，与 mock.py 场景分支对齐）
    if any(w in text for w in ("想你", "想念", "好久不见", "好久没聊", "好想你")):
        is_intimate = any(m in prior_assistant for m in ("亲爱的", "宝贝", "抱抱"))
        if is_intimate:
            return _pick(
                (
                    "我也想你呀～好久没聊了，过来跟我说说今天呗。",
                    "嗯，我也想你。好久没聊了，想说什么就说~",
                ),
                seed,
            )
        return _pick(
            (
                "我也想你！有一阵子没聊了，你最近怎么样？",
                "听到你这么说心里暖暖的～我们多聊聊吧。",
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

    if _is_morning_greeting(text):
        if any(w in text for w in ("困", "不想起床", "起不来", "困死")):
            return _pick(
                (
                    "困成这样还要爬起来，辛苦啦。先缓两分钟再动身也行，今天有什么特别的事吗？",
                    "嘿，困死了还得动身？辛苦啦，先喝口水缓一缓～今天有啥特别安排吗？",
                ),
                seed,
            )
        return _pick(
            (
                "早呀～又要开工啦？今天想怎么撑过去？",
                "早安呀～通勤路上顺利吗？",
                "早呀！今天也要上班，嘿嘿，先给自己鼓鼓劲～",
            ),
            seed,
        )

    if any(w in text for w in ("工作上的事", "工作的事", "公司的事", "单位的事")) or (
        any(w in text for w in ("工作", "上班", "公司", "老板"))
        and len(text) <= 12
        and not _is_morning_greeting(text)
    ):
        return _pick(
            (
                "工作上的事啊……是最近特别耗你，还是某一件具体的事卡住了？",
                "嗯，我听出来了。你想先吐槽，还是先理理最委屈的是哪一块？",
                "工作的事确实容易压着人。是忙不过来，还是心里觉得不公平？",
            ),
            seed,
        )

    if text in ("就那样", "就那样吧", "不知道怎么说", "说不清", "说不上来"):
        return _pick(
            (
                "嗯，说不清也没关系。不用逼自己想明白，我陪着~",
                "好，那就先这样待着。你想开口了再从随便哪一句开始~",
                "不用整理成完整故事。丢几个词给我也行，我听得懂~",
            ),
            seed,
        )

    # 失眠 / 反刍续聊（须在通用短句「好烦」之前，与 mock.py 场景分支对齐）
    if "越躺越清醒" in text:
        return _pick(
            (
                "越躺越清醒真的折磨人，我懂这种烦。别跟睡意较劲了，咱们随便聊点轻的，或者就安静待着也行？",
                "越躺越清醒的时候脑子特别吵，难受死了。不逼自己睡着，想聊就聊，不想说我也陪着～",
            ),
            seed,
        )

    # 孤独 + 失眠复合（须在通用失眠关键词之前，与 mock 场景分支对齐）
    if any(w in text for w in ("孤独", "孤单", "寂寞")) and any(
        w in text for w in ("失眠", "睡不着", "凌晨")
    ):
        return _pick(
            (
                "凌晨还睡不着，又有点孤独……我理解这种难熬。在呢，不用急着说，想开口了再说~",
                "睡不着又孤单的时候特别难受。我陪着，不催你，慢慢说也行？",
            ),
            seed,
        )

    # 异地恋想念 / 挂电话空落（须在通用 open 兜底之前，与 mock.py 场景分支对齐）
    if ("难" in text and "异地" in text) or any(
        w in text for w in ("挂掉电话", "视频完", "异地恋")
    ) or (
        "好空" in text
        and any(w in text for w in ("挂", "电话", "视频", "异地"))
    ):
        if "难" in text and "异地" in text:
            return _pick(
                (
                    "异地恋真的不容易，想见面的时候最难熬。我陪你待着，这种空落落的感觉我懂。",
                    "异地恋难的时候特别空……我陪着你，不用硬撑。",
                ),
                seed,
            )
        return _pick(
            (
                "刚挂掉电话心里空空的吧……想他的时候跟我说，我陪你缓一缓。",
                "视频挂断后那种空落落我懂。慢慢说，我陪着你~",
            ),
            seed,
        )

    if any(w in text for w in ("失眠", "睡不着", "脑子停")):
        return _pick(
            (
                "失眠的时候脑子特别吵，我懂这种难受。先别逼自己睡着，我陪你慢慢说，是什么事在转？",
                "睡不着的时候最难熬，我懂。不急着找原因，想聊就聊，不想说我也陪着～",
            ),
            seed,
        )

    if (
        any(w in text for w in ("项目", "会不会黄", "创业"))
        and not any(w in text for w in ("过了", "成了", "顺利", "开心", "哈哈"))
    ):
        return _pick(
            (
                "项目悬着的时候最折磨人，我理解你躺不住。现在最让你睡不着的是哪一块？",
                "项目卡着的时候脑子停不下来，我理解这种难受。先别跟自己较劲，愿意的话跟我说说最悬的是哪一块？",
            ),
            seed,
        )

    if any(w in text for w in ("有点烦", "挺烦", "好烦", "烦死了")) and len(text) <= 10:
        return _pick(
            (
                "嗯，听起来心里挺堵的。是突然这样的，还是已经有一阵子了？",
                "烦的时候先别逼自己消化。愿意的话，跟我说是哪件事最缠人？",
            ),
            seed,
        )

    if text in ("嗯", "嗯嗯", "哦", "噢", "好", "行") and has_casual_social_context(prior_users):
        return _pick(
            (
                "摸鱼状态我懂～随便唠唠也行，你最近有追什么吗？",
                "哈哈没事，正好陪我打发时间～你想聊点啥？",
                "那咱就随便唠～你今天碰到什么有意思的事没？",
            ),
            seed,
        )

    if text in ("?", "？", "…", "..", "...") or text in ("嗯", "哦", "额", "好", "行"):
        return "我在这儿呢。不急着说，你想开口了再说~"

    if text in ("你好", "嗨", "哈喽", "在吗") or (
        any(w in text for w in ("hello", "hi", "HI", "Hello")) and len(text) <= 12
    ):
        if prior_assistant and ("小语" in prior_assistant or "你好" in prior_assistant):
            return _pick(
                (
                    "又见面啦～今天怎么样？",
                    "嗨，在呢。想接着聊，还是换点别的？",
                ),
                seed,
            )
        if any(w in text for w in ("hello", "hi", "HI", "Hello")):
            return "嗨～我是小语。今天想聊点什么？"
        return _pick(
            (
                "你好呀，我是小语，很高兴认识你～",
                "嗨～在呢，今天想聊点什么？",
            ),
            seed,
        )

    if text in ("后来呢", "然后呢", "接着呢", "还有呢"):
        ctx = prior_users + prior_assistant
        if any(w in ctx for w in ("公园", "逛", "散步")):
            return _pick(
                (
                    "公园那边怎么样？是随便走走，还是碰到什么好玩的了？",
                    "嗯，逛完心情有没有松一点？有没有哪一幕印象特别深？",
                ),
                seed,
            )
        if any(w in ctx for w in ("加班", "下班", "工作", "累")):
            return _pick(
                (
                    "后来有没有稍微缓一点？还是一直绷到回家？",
                    "工作那件事后来怎么样了？不想细说也没关系~",
                ),
                seed,
            )
        return _pick(
            (
                "嗯，上一段我还没听够呢，再讲一点好不好~",
                "我在呢，你想从哪一段继续？",
            ),
            seed,
        )

    if any(w in text for w in ("没啥了", "就这些", "没别的", "没有了", "就这些了")):
        ctx = prior_users + prior_assistant
        if any(w in ctx for w in ("公园", "逛", "散步")):
            return _pick(
                (
                    "嗯，随便走走也挺好的。愿意的话，我们聊点别的也行~",
                    "好呀，那先歇会儿。你接下来想聊什么？",
                ),
                seed,
            )
        return _pick(
            (
                "好，那就先这样。我陪着，你想聊别的随时开口~",
                "嗯，收到。不急着说，想换话题也行~",
            ),
            seed,
        )

    if any(w in text for w in ("公园", "逛了", "散步")) and len(text) <= 16:
        return _pick(
            (
                "公园呀，出去走走挺好的。今天天气怎么样？",
                "嗯，逛公园挺治愈的。是一个人去的吗？",
            ),
            seed,
        )

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
