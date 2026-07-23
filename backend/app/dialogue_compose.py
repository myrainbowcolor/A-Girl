"""开放话题的上下文拼装（scene_first 第二层，无 LLM）。"""
from __future__ import annotations

import hashlib
import re

from .llm.mock import _pet_name_from_context
from .out_of_world_guard import compose_out_of_world_reply, user_asks_out_of_world
from .sentiment_lexicon import (
    contains_keyword,
    has_casual_social_context,
    is_friendly_greeting_utterance,
    is_minimal_fatigue_utterance,
    is_presence_ping_utterance,
    is_positive_utterance,
    user_complains_bot_reply,
)

_MORNING_GREETING_MARKERS = ("早呀", "早安", "早上好", "早啊")
_COMMUTE_MARKERS = ("又要上班", "不想起床", "困死")
_WORK_VENT_MARKERS = ("累", "烦", "加班", "好烦", "好晚", "十点", "九点", "心累", "烦死", "熬")


def _is_morning_greeting(text: str) -> bool:
    """早安/通勤寒暄（非工作压力倾诉）。"""
    t = text.strip()
    if any(v in t for v in _WORK_VENT_MARKERS):
        return False
    if t == "早":
        return True
    if any(m in t for m in _MORNING_GREETING_MARKERS):
        return True
    return any(m in t for m in _COMMUTE_MARKERS)


def _pick(options: tuple[str, ...], seed: str) -> str:
    idx = int(hashlib.md5(seed.encode("utf-8")).hexdigest(), 16) % len(options)
    return options[idx]


def _normalize_stage(stage: str | None) -> str:
    if not stage:
        return ""
    mapping = {
        "stranger": "stranger",
        "陌生": "stranger",
        "acquainted": "acquainted",
        "熟悉": "acquainted",
        "friend": "friend",
        "朋友": "friend",
        "close": "close",
        "亲密": "close",
    }
    key = stage.strip()
    return mapping.get(key, mapping.get(key.lower(), ""))


def _is_intimate_stage(stage: str | None) -> bool:
    return _normalize_stage(stage) == "close"


def _is_friend_stage(stage: str | None) -> bool:
    return _normalize_stage(stage) == "friend"


def _is_intimate_context(prior_assistant: str, relationship_stage: str | None = None) -> bool:
    if _is_intimate_stage(relationship_stage):
        return True
    return any(m in prior_assistant for m in ("亲爱的", "宝贝", "抱抱"))


def _is_warm_friend_context(
    prior_assistant: str, relationship_stage: str | None = None
) -> bool:
    if _is_friend_stage(relationship_stage) or _is_intimate_stage(relationship_stage):
        return True
    return any(
        m in prior_assistant for m in ("开心", "温柔", "真好", "陪你", "随时", "好呀")
    )


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
    relationship_stage: str | None = None,
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
                "不开心的感觉我收到了。我先陪着你，不急着讲道理。",
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

    # 社交探问 NPC 在做什么（须在 open 兜底之前，与 mock.py 场景分支对齐）
    if any(w in text for w in ("你在干嘛", "在干嘛", "干什么")):
        bored_ctx = "无聊" in prior_users
        if bored_ctx:
            return _pick(
                (
                    "刚泡了杯热茶，窝在沙发里发呆呢～你呢，也在摸鱼吗？",
                    "窝在沙发上发呆呢～你这会儿也在摸鱼吗？",
                ),
                seed,
            )
        return _pick(
            (
                "刚泡了杯热茶，窝在沙发里发呆呢～你呢，这会儿忙不忙？",
                "窝在沙发上发呆呢～你这会儿在忙什么吗？",
            ),
            seed,
        )

    # 无聊闲聊首轮（须在 open 兜底之前，与 mock.py 场景分支对齐）
    if any(w in text for w in ("无聊", "没事干", "好闲")):
        if _is_warm_friend_context(prior_assistant, relationship_stage):
            return _pick(
                (
                    "无聊呀？那正好陪我唠会儿～你最近有在追什么剧或玩什么吗？",
                    "摸鱼状态我懂～要不随便唠唠，你最近有追什么剧吗？",
                ),
                seed,
            )
        return _pick(
            (
                "闲下来也行呀。要不随便聊聊，你今天碰到什么有意思的事没？",
                "无聊的时候找我唠唠也行～你今天有什么小事想分享吗？",
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

    if is_minimal_fatigue_utterance(text):
        return _pick(
            (
                "累呀……先别硬撑，缓口气。是身子累还是心里也一起累了？",
                "听着就心疼，累的时候能说出来已经很好了。先歇一会儿，我陪着~",
            ),
            seed,
        )

    # 倚靠倾诉（须在通用负面兜底之前，与 mock.py 场景分支对齐）
    if any(w in text for w in ("靠着", "想靠着", "倚靠")):
        is_intimate = _is_intimate_context(prior_assistant, relationship_stage)
        if is_intimate or "靠着你说" in text:
            return _pick(
                (
                    "过来，靠着我慢慢说。今天辛苦了，我哪儿也不去。",
                    "靠过来吧。累的时候不用硬撑，想说什么就说~",
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

    # 养宠物 / 分享毛孩子（须在捣蛋续聊之前，与 mock.py 场景分支对齐）
    if any(w in text for w in ("猫", "狗", "宠物")) and "记得" not in text:
        if "猫" in text:
            return _pick(
                (
                    "养猫呀！粘人的小家伙最会撒娇了～它平时最爱干嘛，是跟着你还是搞破坏？",
                    "有猫陪着日子都软一点～粘人的那种最会缠人了，它平时爱干什么？",
                ),
                seed,
            )
        return _pick(
            (
                "有毛孩子陪着，日子都会软一点。它性格怎么样？",
                "养宠物真好呀～它平时黏你还是酷酷的那种？",
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
                    f"哈哈，{refer}搞破坏啦？又气又好笑，易碎的东西可得收一收～它这会儿怂了没？",
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
        if _is_intimate_context(prior_assistant, relationship_stage):
            return _pick(
                (
                    "我也想你呀～好久没聊了，过来跟我说说今天呗。",
                    "我也想你。好久没聊了，想说什么就说~",
                ),
                seed,
            )
        if _is_friend_stage(relationship_stage):
            return _pick(
                (
                    "我也想你！有一阵子没聊了，你最近怎么样？",
                    "好久不见呀，听到你这么说心里暖暖的～我们多聊聊吧。",
                ),
                seed,
            )
        return _pick(
            (
                "听到你这么说心里暖暖的～我们多聊聊吧。",
                "我也挺想跟你多聊聊的。你最近怎么样？",
            ),
            seed,
        )

    # 还想继续聊（须在「哈哈」报喜之前，与 mock.py 场景分支对齐）
    if any(w in text for w in ("还想", "明天", "下次")) and any(
        w in text for w in ("聊", "找", "来")
    ):
        is_intimate = _is_intimate_context(prior_assistant, relationship_stage)
        is_warm_friend = _is_warm_friend_context(prior_assistant, relationship_stage)
        if is_intimate or is_warm_friend:
            return _pick(
                (
                    "好呀，我随时都在～你想聊的时候来找我就行，我很开心你愿意再来。",
                    "好呀～你想聊的时候来找我就行，能陪你说话我也很开心。",
                ),
                seed,
            )
        return _pick(
            (
                "好呀～明天想聊就来找我，能陪你说话我也很开心。",
                "好呀，明天想来聊就来～能陪你说话我也挺开心的。",
            ),
            seed,
        )

    # 天气 / 电影闲聊（须在开心分享之前，与 mock.py 场景分支对齐）
    if any(w in text for w in ("天气", "电影", "不错", "挺好")) and len(text) <= 16:
        if "电影" in text:
            return _pick(
                (
                    "什么片子呀？好看的话给我也安利一下～",
                    "看的啥电影？好看不，给我也说说～",
                ),
                seed,
            )
        if "天气" in text:
            return _pick(
                (
                    "是吧，这种天出门心情都会好一点。你今天有出去晒晒太阳吗？",
                    "好天气确实让人松口气。你今天有出去走走吗？",
                ),
                seed,
            )
        return _pick(
            (
                "听着就挺舒服的～今天有啥小开心的事吗？",
                "今天还不错～有什么让你印象深的小事吗？",
            ),
            seed,
        )

    # 感谢（须在 is_positive_utterance 开心分享之前，与 mock.py 场景分支对齐）
    if any(w in text for w in ("谢谢", "感谢", "多谢")):
        if _is_intimate_stage(relationship_stage) or _is_friend_stage(relationship_stage):
            return _pick(
                (
                    "跟我还客气什么呀，能帮到你我就很开心了。",
                    "别跟我见外～你愿意跟我说这些，我也挺高兴的。",
                ),
                seed,
            )
        return _pick(
            (
                "不客气呀，你愿意跟我说这些，我也挺高兴的。",
                "客气啥～能帮上一点忙我就很开心了。",
            ),
            seed,
        )

    # 晚安 / 道别（与 mock.py 场景分支对齐）
    if any(w in text for w in ("晚安", "睡了", "再见", "拜拜", "先走了")):
        if _is_intimate_stage(relationship_stage) or _is_friend_stage(relationship_stage):
            return _pick(
                (
                    "晚安呀，做个好梦～明天再来找我聊好不好？",
                    "晚安～好好休息，明天想聊再来找我。",
                ),
                seed,
            )
        return _pick(
            (
                "嗯，晚安～好好休息，下次再聊。",
                "好，晚安呀～好好睡一觉。",
            ),
            seed,
        )

    # 开心分享（须在「哈哈」报喜之前，与 mock.py 场景分支对齐）
    if is_positive_utterance(text):
        if "城市" in text and any(w in text for w in ("去", "搬", "喜欢", "期待")):
            return _pick(
                (
                    "要去喜欢的城市呀，光听着就替你开心！那边有什么你最期待的事？",
                    "能去喜欢的城市真好～听着就替你高兴，那边你最期待啥？",
                ),
                seed,
            )
        is_intimate = _is_intimate_context(prior_assistant, relationship_stage)
        is_warm_friend = _is_warm_friend_context(prior_assistant, relationship_stage)
        if is_intimate or is_warm_friend:
            return _pick(
                (
                    "哇，听你这么说我也跟着开心起来了！快多跟我说说～",
                    "太棒了！替你开心～后来怎么样了？",
                ),
                seed,
            )
        return _pick(
            (
                "真好呀，看到你开心我也觉得暖暖的～",
                "听着就替你高兴！愿意的话多跟我说说～",
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
                "早呀～又要开工啦？",
                "早安呀～通勤路上顺利吗？",
                "早呀！今天也要上班，嘿嘿，先给自己鼓鼓劲～",
            ),
            seed,
        )

    # 怀旧 / 童年（须在通用负面 open 兜底之前，与 mock.py 场景分支对齐）
    if any(w in text for w in ("怀念", "小时候", "外婆", "童年", "汤圆", "旧时光")):
        if any(w in text for w in ("简单", "静下来", "现在好难")):
            return _pick(
                (
                    "现在节奏这么快，能安静下来的时刻确实少了。要是能偶尔像小时候那样慢下来，你想先做什么？",
                    "日子一快起来，能静下来的时候就少了……要是偶尔像小时候那样慢下来，你想先做什么？",
                ),
                seed,
            )
        return _pick(
            (
                "突然想到那些旧时光，心里会又暖又酸吧。外婆的汤圆是什么馅的？跟我多说说那时候的事。",
                "想到小时候那些事，心里又暖又酸的吧。汤圆是什么馅的？多跟我说说那时候~",
            ),
            seed,
        )
    if any(w in text for w in ("简单", "静下来", "现在好难")) and any(
        w in prior_users for w in ("怀念", "外婆", "童年", "汤圆", "旧时光", "小时候")
    ):
        return _pick(
            (
                "现在节奏这么快，能安静下来的时刻确实少了。要是能偶尔像小时候那样慢下来，你想先做什么？",
                "日子一快起来，能静下来的时候就少了……要是偶尔像小时候那样慢下来，你想先做什么？",
            ),
            seed,
        )

    # 育儿 / 哄娃疲惫（须在加班疲惫与通用负面 open 兜底之前，与 mock.py 场景分支对齐）
    if any(w in text for w in ("哄娃", "带娃", "神兽", "孩子闹")) and any(
        w in text for w in ("累", "辛苦", "撑", "心累", "好累")
    ):
        return _pick(
            (
                "一边上班一边顾娃，真的太耗你了……你先歇会儿，我陪着你。今天最累的是哪一会儿？",
                "下班还要哄娃，真的太累了……你先缓口气，我陪着你。是哪一段最耗你？",
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

    # 加班 / 下班疲惫倾诉（须在「好烦」短句与通用负面 open 兜底之前，与 mock.py 场景分支对齐）
    if any(w in text for w in ("加班", "下班", "十点", "很晚", "熬夜", "996", "KPI", "开会到")) and any(
        w in text for w in ("累", "烦", "辛苦", "熬", "撑", "心累", "好累", "好烦")
    ) or (
        "下班" in text
        and any(w in text for w in ("累", "烦", "十点", "九点", "很晚", "好晚"))
    ):
        is_intimate = _is_intimate_context(prior_assistant, relationship_stage)
        if is_intimate:
            return _pick(
                (
                    "又加班到这么晚，真的辛苦你了……今天先别跟自己较劲，缓口气再说好不好？",
                    "听着就心疼，又熬到这么晚……先歇会儿，我陪着你。",
                ),
                seed,
            )
        return _pick(
            (
                "加班熬到这么晚，真的辛苦你了……今天先别跟自己较劲，缓口气再说好不好？",
                "又熬到这么晚呀，听着就累……不用急着讲细节，我在这儿陪着你。",
            ),
            seed,
        )

    # emo / 丧 / 心累低落（须在育儿/加班等具体分支之后，与 mock.py 场景分支对齐）
    if any(w in text.lower() for w in ("emo", "丧")) or any(w in text for w in ("心累", "心好累")):
        return _pick(
            (
                "这种低落的感觉我懂。不想硬撑的时候，就陪我随便聊聊也好。",
                "低落的时候不用硬撑。我陪着，你想说就说~",
            ),
            seed,
        )

    # 考试 / 学业焦虑（须在通用负面 open 兜底之前，与 mock.py 场景分支对齐）
    if not any(w in text for w in ("孩子", "他", "她", "儿子", "女儿")) and any(
        w in text for w in ("紧张", "焦虑", "记不住", "考不上", "高考", "考试", "期末", "考研")
    ):
        if "记不住" in text:
            return _pick(
                (
                    "记不住的时候别跟自己较劲，我理解这种焦虑。大脑也需要喘口气，是某一科特别卡，还是整体都觉得乱？",
                    "什么都记不住的时候最容易慌，我理解。先别逼自己，是复习量太大，还是某一科特别卡？",
                ),
                seed,
            )
        return _pick(
            (
                "考前紧张太正常了，我理解你现在心里绷着弦。先别急着否定自己，是复习节奏乱了，还是心里压力更大？",
                "高考前心里绷着弦太正常了，我理解你这种紧张。是复习节奏乱了，还是压力主要来自心里？",
            ),
            seed,
        )

    # 育儿焦虑（家长视角）（须在通用负面 open 兜底之前，与 mock.py 场景分支对齐）
    if any(w in text for w in ("孩子", "儿子", "女儿", "太严厉", "耽误", "考不好")):
        if any(w in text for w in ("耽误", "害怕", "怕")):
            return _pick(
                (
                    "你怕耽误他，说明你是真的在乎，我理解这种担心。具体是哪一点让你最睡不着？",
                    "怕耽误孩子的时候，这种焦虑压在心里最难受……你最担心的是哪一点？",
                ),
                seed,
            )
        return _pick(
            (
                "当家长这么操心，我真的心疼你……你已经很在乎 ta 了。跟我说说你最担心的是什么？",
                "孩子考得不好就怪自己太严厉，我理解这种自责……你先别急着怪自己，最让你揪心的是哪一块？",
            ),
            seed,
        )

    # 失恋 / 分手倾诉（须在通用负面 open 兜底之前，与 mock.py 场景分支对齐）
    breakup_context = any(
        w in prior_users + text for w in ("分手", "失恋", "分开", "分开了")
    )
    if any(w in text for w in ("分手", "失恋", "分开了")):
        return _pick(
            (
                "哎……分手真的很难扛。你别一个人硬撑，我陪你待着，想说多少说多少。",
                "听到你说分手了，我心里也沉了一下。分手这种事真的很耗人，你不用装作没事。",
            ),
            seed,
        )
    if any(w in text for w in ("想哭", "哭了", "忍不住哭")) and breakup_context:
        return _pick(
            (
                "想哭就哭出来吧，不用忍着。分手这种事真的很耗人，我陪着你，想说多少说多少。",
                "哭出来也没关系，不用在我面前装坚强。我陪着你，想说多少说多少。",
            ),
            seed,
        )
    if any(w in text for w in ("好起来", "会好")) and ("?" in text or "吗" in text):
        return _pick(
            (
                "这种时候会怀疑自己，我特别理解。你不用急着给答案，我陪你一天一天慢慢来，好吗？",
                "难过的时候不用急着好起来，我陪你待着就好。我们慢慢来，不着急。",
            ),
            seed,
        )

    # 生病 / 身体不适（须在通用负面 open 兜底之前，与 mock.py 场景分支对齐）
    if any(w in text for w in ("感冒", "发烧", "生病", "头痛", "头疼", "不舒服")):
        is_intimate = _is_intimate_context(prior_assistant, relationship_stage)
        if is_intimate:
            return _pick(
                (
                    "怎么又生病了……头还痛不痛？今天乖乖躺着，我陪着你，难受就跟我说。",
                    "生病还难受着呀……今天就别硬撑了，我陪着你，哪里最不舒服？",
                ),
                seed,
            )
        return _pick(
            (
                "生病还头痛呀，听着就心疼……今天别硬撑，我陪着你，哪里最难受？",
                "感冒还难受着呀，辛苦你了……今天先好好休息，我陪着你，现在最难受的是哪一块？",
            ),
            seed,
        )

    # 节日孤独 / 想家（须在通用负面 open 兜底之前，与 mock.py 场景分支对齐）
    if any(w in text for w in ("落寞", "团圆", "过年", "一个人")):
        if any(w in text for w in ("团圆", "更难受", "看到别人")):
            return _pick(
                (
                    "看到别人团圆，对比之下确实会更扎心。这种时候别怪自己敏感，我陪你待着，想说就说。",
                    "看到别人团圆会更难熬，这种对比我懂。别怪自己敏感，我在这儿陪着你。",
                ),
                seed,
            )
        return _pick(
            (
                "一个人过节确实会空落落的……听起来你挺想家的。这种时候难受很正常，我陪你待着，慢慢说。",
                "过节一个人待着，心里会空落落的吧。难受很正常，我陪你待着，想说就说~",
            ),
            seed,
        )

    if text in (
        "就那样",
        "就那样吧",
        "不知道怎么说",
        "说不清",
        "说不上来",
        "不知道",
        "说不上",
    ):
        return _pick(
            (
                "说不清也没关系，不用逼自己想明白。我陪着，从哪一句开始都行~",
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

    # 比较 / 自我怀疑（须在通用负面 open 兜底之前，与 mock.py 场景分支对齐）
    if any(w in text for w in ("升职", "原地踏步", "差劲", "不如")):
        if any(w in text for w in ("差劲", "太差")):
            return _pick(
                (
                    "别急着给自己贴「差劲」的标签，我理解这种自我怀疑。你现在是跟同学比，还是跟以前的自己比？",
                    "自我怀疑冒出来的时候真的难受。先别急着否定自己，你愿意说说最堵的是哪一点？",
                ),
                seed,
            )
        return _pick(
            (
                "跟别人一比就否定自己，这种落差真的很难受。我不是要灌鸡汤，就想听听你现在最堵的是哪一点？",
                "比较之后觉得自己停在原地，这种感受我懂。不急着反驳，你此刻最难受的是哪一块？",
            ),
            seed,
        )

    # 冲动消费后悔 / 自责（须在通用负面 open 兜底之前，与 mock.py 场景分支对齐）
    if any(w in text for w in ("乱花钱", "管不住", "没用", "后悔")) and any(
        w in text for w in ("钱", "买", "手", "花", "没用")
    ):
        if any(w in text for w in ("没用", "管不住手")):
            return _pick(
                (
                    "别急着骂自己没用，谁都有失手的时候。我陪着你，这次最让你后悔的是哪一点？",
                    "管不住手的时候最容易骂自己，我心疼你。先别急着贴标签，愿意说说这次是什么情况？",
                ),
                seed,
            )
        return _pick(
            (
                "后悔的时候最容易骂自己，我心疼你。先别急着贴标签，跟我说说这次是什么让你没忍住？",
                "乱花钱之后骂自己最难受了。我陪着你，不急着说教，你想从哪一句说起？",
            ),
            seed,
        )

    # 吵架 / 冷战 / 和好别扭（须在通用负面 open 兜底之前，与 mock.py 场景分支对齐）
    fight_context = any(
        w in prior_users + text
        for w in ("吵架", "冷战", "对象", "伴侣", "拉不下脸", "和好", "别扭")
    )
    if any(w in text for w in ("吵架", "冷战", "不理谁", "对象", "伴侣", "拉不下脸")) or (
        any(w in text for w in ("先发", "要不要", "消息", "发消息")) and fight_context
    ):
        if any(w in text for w in ("先发", "要不要", "消息", "发消息")):
            return _pick(
                (
                    "想台阶又拉不下脸，这种别扭我理解。不用完美措辞，一句「我们聊聊」有时就够了。你想怎么开口？",
                    "别扭的时候最难开口……不用写小作文，简单一句也行。你想先发什么？",
                ),
                seed,
            )
        if any(w in text for w in ("我的问题", "拉不下脸")):
            return _pick(
                (
                    "能想到自己也有问题，说明你其实想和好。别扭的时候最难，我陪你理理现在最卡的是哪一点？",
                    "愿意承认自己有部分原因，其实已经往前迈了一步。现在最拉不下脸的是哪一块？",
                ),
                seed,
            )
        return _pick(
            (
                "吵架后的沉默最磨人……现在心里是气多，还是委屈多？慢慢说，我听着呢。",
                "冷战的时候最难熬，我懂。你现在更想先发泄，还是先理理委屈？",
            ),
            seed,
        )

    # 被责骂 / 愤怒发泄（须在通用负面 open 兜底之前，与 mock.py 场景分支对齐）
    if any(w in text for w in ("气死", "骂我", "骂", "老板")) or (
        "辞职" in text
        and ("想" in text or "要" in text or "立刻" in text)
        and "信" not in text
    ):
        if "辞职" in text and ("想" in text or "立刻" in text) and "信" not in text:
            return _pick(
                (
                    "冲动辞职的念头我理解，但先别急着做决定。今晚先把自己从气里捞出来，明天清醒了再想想？",
                    "想立刻走的心情我理解，先别在气头上做决定。今晚缓一缓，我陪着你，明天清醒了再想想？",
                ),
                seed,
            )
        return _pick(
            (
                "当众被骂真的太过分了，我能理解你现在又气又委屈。先别急着做决定，我陪你把这股火慢慢说出来。",
                "被骂的时候又气又委屈，我懂。先别急着做决定，我陪着你慢慢说~",
            ),
            seed,
        )

    # 防御心态 / 觉得没人懂（须在通用负面 open 兜底之前，与 mock.py 场景分支对齐）
    if any(w in text for w in ("你不懂", "没人懂", "不懂我")):
        return _pick(
            (
                "我听见你的委屈了……可能我没完全懂，但我在认真听。你愿意的话，慢慢跟我说，我想更懂一点。",
                "你说没人懂的时候，我心里也揪了一下。我可能没全懂，但我在认真听，你想说多少都行。",
            ),
            seed,
        )

    # 快撑不住了 / 倦怠极限（须在通用负面 open 兜底之前，与 mock.py 场景分支对齐）
    if any(w in text for w in ("撑不住", "扛不住", "受不了")):
        return _pick(
            (
                "听起来你真的快到极限了……先别一个人硬撑，我陪着你。慢慢说，是什么让你这么累？",
                "快到极限的时候别一个人扛……我陪着你，你想说多少都行。",
            ),
            seed,
        )

    if any(w in text for w in ("有点烦", "挺烦", "好烦", "烦死了")) and len(text) <= 10:
        return _pick(
            (
                "听起来心里挺堵的。不想说原因也没关系，我在呢——愿意的话，是什么事最缠人？",
                "烦的时候先别逼自己消化。我陪着你，愿意的话跟我说说是哪件事最缠人？",
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

    if is_friendly_greeting_utterance(text) or is_presence_ping_utterance(text) or text in (
        "你好",
        "嗨",
        "哈喽",
    ) or (any(w in text for w in ("hello", "hi", "HI", "Hello")) and len(text) <= 12):
        if prior_assistant and ("小语" in prior_assistant or "你好" in prior_assistant):
            return _pick(
                (
                    "又见面啦～今天怎么样？",
                    "嗨，在呢。想接着聊，还是换点别的？",
                ),
                seed,
            )
        if is_presence_ping_utterance(text) and not is_friendly_greeting_utterance(text):
            return _pick(
                (
                    "在呢～我听着，今天想聊点什么？",
                    "在呢，来啦～有什么想说的？",
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

    if any(w in text for w in ("不愿意", "不想聊", "别说了", "不想说", "不说了", "算了")):
        return _pick(
            (
                "不想说也没关系，我陪着你。什么时候想开口了，我都在。",
                "好，不聊也行。我陪着，你想说的时候再说~",
            ),
            seed,
        )

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
