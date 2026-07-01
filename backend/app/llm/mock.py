"""离线 Mock Provider（仅 pytest / CI）。

生产对话请用 scene_first + SceneReplyEngine + 本地 LLM，勿将 AGIRL_LLM_PROVIDER 设为 mock。
场景分支逻辑见 app/scene_engine.py / llm/mock.generate_scene_reply。
"""
from __future__ import annotations

import hashlib
import re

from .base import LLMProvider
from ..sentiment_lexicon import (
    contains_keyword,
    contains_any,
    has_casual_social_context,
    is_positive_utterance,
    user_complains_bot_reply,
)

# 用户情绪线索（与 emotion.engine 词典呼应，Mock 侧做共情话术）
# 注意：「无聊」不算倾诉，走闲聊分支
_VENT = (
    "烦", "累", "难过", "伤心", "生气", "委屈", "焦虑", "崩溃", "孤独",
    "压力", "糟糕", "不开心", "想哭", "绝望", "讨厌", "分手", "哭了", "哭",
    "气死", "落寞", "难受", "骂", "辞职", "严厉", "害怕", "耽误",
    "原地踏步", "踏步", "emo", "丧", "心累", "没用", "自卑", "迷茫", "憋着",
)
_LOW = ("低落", "没劲", "丧", "emo", "心累")
_POSITIVE = (
    "开心", "高兴", "喜欢", "谢谢", "哈哈", "棒", "幸福", "温暖", "想你",
    "offer", "录取", "通过", "中了", "dream",
)
_GREET = ("你好", "嗨", "在吗", "哈喽", "早上好", "晚上好")


def _extract(tag: str, text: str, default: str = "") -> str:
    m = re.search(rf"{tag}：(.+)", text)
    if not m:
        return default
    # 关系阶段等字段可能带括号后缀，只取首段
    return m.group(1).strip().split("（")[0].strip()


def _user_is_venting(text: str) -> bool:
    t = text.strip()
    return any(w in t for w in _VENT) or any(w in t for w in _LOW)


def _user_is_positive(text: str) -> bool:
    return is_positive_utterance(text)


def _user_is_greeting(text: str) -> bool:
    t = text.strip()
    return len(t) <= 8 and any(w in t for w in _GREET)


def _extract_memories(system_prompt: str) -> list[str]:
    """从 system 提示中解析检索到的记忆条目。"""
    m = re.search(r"【关于 ta 的已知事实[^】]*】\n(.*?)\n\n【", system_prompt, re.DOTALL)
    if not m:
        return []
    block = m.group(1).strip()
    if "暂无" in block or "暂时还没有" in block:
        return []
    return [line[2:].strip() for line in block.split("\n") if line.startswith("- ")]


def _user_tone(text: str) -> str:
    """粗分用户话语意图，驱动更拟真的回复模板。"""
    t = text.strip()
    if any(w in t for w in ("你好", "嗨", "哈喽", "在吗", "早上好", "晚上好")):
        return "greet"
    if "?" in t or "？" in t or any(w in t for w in ("吗", "呢", "什么", "怎么", "为什么", "哪")):
        return "question"
    if any(w in t for w in (
        "难过", "伤心", "累", "烦", "孤独", "压力", "焦虑", "崩溃", "哭",
        "不开心", "委屈", "分手", "失恋", "原地踏步", "踏步", "自卑", "迷茫",
    )):
        return "negative"
    if is_positive_utterance(t):
        return "positive"
    if any(w in t for w in ("我", "今天", "刚才", "最近")) and len(t) >= 8:
        return "share"
    return "neutral"


def _memory_hook(memories: list[str], user_text: str) -> str:
    """若记忆与用户话有词重叠，抽一句自然引用。"""
    if not memories:
        return ""
    user_chars = set(user_text)
    best, best_score = "", 0
    for mem in memories:
        overlap = sum(1 for ch in mem if ch in user_chars and len(ch.strip()) > 0)
        if overlap > best_score:
            best_score, best = overlap, mem
    if best_score < 2:
        return ""
    # 去掉 "ta 说：" 前缀，让引用更口语
    snippet = best.replace("ta 说：", "").strip()
    if len(snippet) > 24:
        snippet = snippet[:24] + "…"
    return f"对了，我还记得你提过「{snippet}」。"


def _pick_variant(options: list[str], seed: str) -> str:
    if not options:
        return ""
    idx = int(hashlib.md5(seed.encode("utf-8")).hexdigest(), 16) % len(options)
    return options[idx]


def _pet_name_from_context(user_hist: str, memories: list[str]) -> str | None:
    """从用户历史或记忆中提取宠物名；有种别但无名字时返回空字符串；无宠物语境返回 None。"""
    combined = f"{user_hist} {' '.join(memories)}"
    if not any(w in combined for w in ("猫", "狗", "宠物")):
        return None
    m = re.search(r"叫(.+?)的(?:猫|狗)", combined)
    return m.group(1) if m else ""


def _format_memory_recall(mem: str, user_text: str) -> str:
    """把记忆条目口语化引用，避免复读「ta 说：」原文。"""
    raw = mem.replace("ta 说：", "").strip()
    if any(w in user_text for w in ("猫", "狗", "宠物", "叫什么")):
        m = re.search(r"叫(.+?)的(?:猫|狗)", raw)
        if m:
            pet_name = m.group(1)
            kind = "小猫" if "猫" in raw or "猫" in user_text else "小狗"
            return f"当然记得呀，你的{kind}叫{pet_name}～"
    if len(raw) <= 22:
        return f"当然记得呀，{raw}"
    return f"当然记得呀，{raw[:22]}……"


def _clean_label(raw: str) -> str:
    """去掉括号内的数值说明，保留可读标签。"""
    return raw.split("（")[0].strip()


def _mood_prefix(emotion: str, seed: str = "") -> str:
    key = seed or emotion
    if any(w in emotion for w in ("低落", "委屈", "焦虑")):
        return _pick_variant(
            ("（轻轻叹了口气）", "（声音放轻了些）", "（安静了一会儿）"),
            key + ":sad",
        )
    if any(w in emotion for w in ("开心", "兴奋", "满足")):
        return _pick_variant(
            ("（眼睛亮了起来）", "（忍不住弯了弯嘴角）", "（语气轻快起来）"),
            key + ":happy",
        )
    if "平和" in emotion:
        return ""
    return _pick_variant(("（微微歪头）", "（认真听着）"), key + ":neutral")


def _scene_mood(emotion: str, user_text: str) -> str:
    """用户倾诉时优先用安抚神态，避免 NPC 内在开心时却「弯嘴角」。"""
    if any(w in user_text for w in ("怀念", "小时候", "外婆", "童年", "旧时光")):
        return _pick_variant(
            ("（声音放轻了些）", "（语气柔软下来）", "（微微弯了弯嘴角）"),
            user_text + ":nostalgic",
        )
    if _user_is_venting(user_text) or any(
        w in user_text for w in ("累", "辛苦", "撑", "难过", "烦", "孤独", "空")
    ):
        return _pick_variant(
            ("（轻轻叹了口气）", "（声音放轻了些）", "（安静了一会儿）"),
            user_text + ":comfort",
        )
    return _mood_prefix(emotion, user_text)


def _endearment(stage: str) -> str:
    return {
        "陌生": "",
        "熟悉": "",
        "朋友": "嘿，",
        "亲密": "亲爱的，",
    }.get(stage, "")


def _prior_assistant(messages: list[dict]) -> str:
    for m in reversed(messages):
        if m["role"] == "assistant":
            return m["content"]
    return ""


def _user_turn_count(messages: list[dict]) -> int:
    return sum(1 for m in messages if m["role"] == "user")


def _scene_reply(
    user_last: str,
    emotion: str,
    stage: str,
    name: str,
    memories: list[str],
    *,
    messages: list[dict] | None = None,
) -> str | None:
    """按用户意图匹配场景化回复；未命中返回 None 走通用模板。"""
    text = user_last.strip()
    dear = _endearment(stage)
    mood = _scene_mood(emotion, text)
    prior = _prior_assistant(messages or [])
    turn_no = _user_turn_count(messages or [])

    # 用户纠正 NPC 接话（应先安慰、别跑题回忆）
    if user_complains_bot_reply(text):
        return _pick_variant(
            [
                f"{dear}{mood}对不起，刚才确实是我没接对。你现在不开心的感受我听见了，"
                f"我先陪着你，不急着扯别的。",
                f"{dear}{mood}你说得对，我应该先安慰你。抱歉刚才跑偏了——"
                f"此刻你最难受的是哪一块？",
                f"{dear}{mood}嗯，是我刚才没接住。先别管回忆那些事了，我在这儿，"
                f"你想怎么说都行。",
            ],
            text + prior,
        )

    # 不开心（须在「开心报喜」分支之前）
    if contains_keyword(text, "不开心") or text in ("我不开心", "我不高兴了"):
        return _pick_variant(
            [
                f"{dear}{mood}嗯……不开心的感觉我收到了。我先陪着你，不急着讲道理。",
                f"{dear}{mood}听起来你现在心里挺沉的。对不起如果刚才没接对，我在呢。",
                f"{dear}{mood}我听见你不开心了。先缓口气，我哪儿也不去。",
            ],
            text + stage,
        )

    # 问候
    if re.search(r"^(你好|嗨|哈喽|hello|hi)", text, re.I):
        if stage == "亲密":
            return f"{dear}{mood}你来啦，我正想着你呢～今天怎么样呀？"
        if stage == "朋友":
            return f"{dear}{mood}嗨！又见面啦，最近忙不忙？"
        return f"{mood}你好呀，我是{name}，很高兴认识你～"

    # 加班 / 下班疲惫
    if any(w in text for w in ("加班", "下班", "十点", "很晚", "熬夜")) and any(
        w in text for w in ("累", "烦", "辛苦", "熬", "撑")
    ):
        return (
            f"{dear}{mood}加班熬到这么晚，真的辛苦你了……"
            f"今天先别跟自己较劲，缓口气再说好不好？"
        )

    # 育儿 / 哄娃疲惫
    if any(w in text for w in ("哄娃", "带娃", "神兽", "孩子闹")) and any(
        w in text for w in ("累", "辛苦", "撑", "心累", "好累")
    ):
        return (
            f"{dear}{mood}一边上班一边顾娃，真的太耗你了……"
            f"你先歇会儿，我陪着你。今天最累的是哪一会儿？"
        )

    # 用户在问 NPC 在做什么
    if any(w in text for w in ("你在干嘛", "在干嘛", "干什么")):
        return (
            f"{dear}{mood}刚泡了杯热茶，窝在沙发里发呆呢～你呢，"
            f"{'也在摸鱼吗' if '无聊' in prior else '这会儿忙不忙'}？"
        )

    # 养宠物 / 分享毛孩子
    if any(w in text for w in ("猫", "狗", "宠物")) and "记得" not in text:
        if "猫" in text:
            return (
                f"{dear}{mood}养猫呀！粘人的小家伙最会撒娇了～"
                f"它平时最爱干嘛，是跟着你还是搞破坏？"
            )
        return f"{dear}{mood}有毛孩子陪着，日子都会软一点。它性格怎么样？"

    # 宠物捣蛋续聊（代词「它」+ 上文有宠物语境，优先于通用「哈哈」开心分支）
    user_hist = " ".join(m["content"] for m in (messages or []) if m["role"] == "user")
    pet_name = _pet_name_from_context(user_hist, memories)
    if (
        pet_name is not None
        and "它" in text
        and any(w in text for w in ("打翻", "杯子", "搞破坏", "淘气", "拆家"))
    ):
        refer = pet_name if pet_name else "小家伙"
        if "打翻" in text or "杯子" in text:
            return (
                f"{dear}{mood}哈哈，{refer}又把杯子打翻啦？"
                f"这种捣蛋精真是又气又好笑～它现在躲起来了吗？"
            )
        return (
            f"{dear}{mood}哈哈，{refer}又淘气了～"
            f"今天怎么这么有精神呀？"
        )

    # 怀旧 / 童年
    if any(w in text for w in ("怀念", "小时候", "外婆", "童年", "汤圆")):
        if any(w in text for w in ("简单", "静下来", "现在好难")):
            return (
                f"{dear}{mood}嗯……现在节奏这么快，能安静下来的时刻确实少了。"
                f"要是能偶尔像小时候那样慢下来，你想先做什么？"
            )
        return (
            f"{dear}{mood}突然想到那些旧时光，心里会又暖又酸吧。"
            f"外婆的汤圆是什么馅的？跟我多说说那时候的事。"
        )
    if any(w in text for w in ("简单", "静下来", "现在好难")) and any(
        w in prior for w in ("怀念", "外婆", "童年", "汤圆", "旧时光")
    ):
        return (
            f"{dear}{mood}嗯……现在节奏这么快，能安静下来的时刻确实少了。"
            f"要是能偶尔像小时候那样慢下来，你想先做什么？"
        )

    # 天气 / 日常小事
    if any(w in text for w in ("天气", "电影", "不错", "挺好")) and len(text) <= 16:
        if "电影" in text:
            return f"{dear}{mood}什么片子呀？好看的话给我也安利一下～"
        if "天气" in text:
            return f"{dear}{mood}是吧，这种天出门心情都会好一点。你今天有出去晒晒太阳吗？"
        return f"{dear}{mood}嗯嗯，听起来今天还不错～有什么让你印象深的小事吗？"

    # 加班 / 工作压力
    if any(w in text for w in ("加班", "996", "KPI", "开会到")) or (
        "下班" in text and any(w in text for w in ("累", "烦", "十点", "九点", "很晚", "好晚"))
    ):
        if stage == "陌生":
            return (
                f"{mood}又熬到这么晚呀，真的辛苦你了。"
                f"不用急着讲细节，我在这儿陪着你。"
            )
        if stage == "熟悉":
            return (
                f"{dear}{mood}又加班啦？听着就累……"
                f"先缓口气，是事情堆太多，还是纯粹耗到这么晚？"
            )
        return (
            f"{dear}{mood}又加班到这么晚，心疼你。"
            f"今天最耗你的是哪一块，跟我说说？"
        )

    # 失眠 / 反复想事
    if "越躺越清醒" in text:
        return (
            f"{dear}{mood}越躺越清醒真的折磨人，我懂这种烦。"
            f"别跟睡意较劲了，咱们随便聊点轻的，或者就安静待着也行？"
        )

    if any(w in text for w in ("失眠", "睡不着", "脑子停")):
        return (
            f"{dear}{mood}失眠的时候脑子特别吵，我懂这种难受。"
            f"先别逼自己睡着，我陪你慢慢说，是什么事在转？"
        )

    # 项目 / 创业焦虑（排除正向报喜语境）
    if (
        any(w in text for w in ("项目", "会不会黄", "创业"))
        and not _user_is_positive(text)
        and "过了" not in text
    ):
        return (
            f"{dear}{mood}项目悬着的时候最折磨人，我理解你躺不住。"
            f"现在最让你睡不着的是哪一块？"
        )

    # 吵架 / 冷战
    fight_context = any(
        w in (prior + " ".join(m.get("content", "") for m in (messages or []) if m["role"] == "user"))
        for w in ("吵架", "冷战", "对象", "伴侣", "拉不下脸", "和好", "别扭")
    )
    if any(w in text for w in ("吵架", "冷战", "不理谁", "对象", "伴侣", "拉不下脸")) or (
        any(w in text for w in ("先发", "要不要", "消息", "发消息")) and fight_context
    ):
        if any(w in text for w in ("先发", "要不要", "消息", "发消息")):
            return (
                f"{dear}{mood}想台阶又拉不下脸，这种别扭我理解。"
                f"不用完美措辞，一句「我们聊聊」有时就够了。你想怎么开口？"
            )
        if any(w in text for w in ("我的问题", "拉不下脸")):
            return (
                f"{dear}{mood}能想到自己也有问题，说明你其实想和好。"
                f"别扭的时候最难，我陪你理理现在最卡的是哪一点？"
            )
        return (
            f"{dear}{mood}吵架后的沉默最磨人……现在心里是气多，还是委屈多？"
            f"慢慢说，我听着呢。"
        )

    # 冲动消费 / 自责
    if any(w in text for w in ("乱花钱", "管不住", "没用", "后悔")) and any(
        w in text for w in ("钱", "买", "手", "花", "没用")
    ):
        if any(w in text for w in ("没用", "管不住手")):
            return (
                f"{dear}{mood}别急着骂自己没用，谁都有失手的时候。"
                f"我陪着你，这次最让你后悔的是哪一点？"
            )
        return (
            f"{dear}{mood}后悔的时候最容易骂自己，我心疼你。"
            f"先别急着贴标签，跟我说说这次是什么让你没忍住？"
        )

    # emo / 丧 — 低落口语
    if any(w in text.lower() for w in ("emo", "丧")) or "心累" in text:
        return (
            f"{dear}{mood}嗯……这种低落的感觉我懂。"
            f"不想硬撑的时候，就陪我随便聊聊也好。"
        )

    # 比较 / 自我怀疑
    if any(w in text for w in ("升职", "原地踏步", "差劲", "不如")):
        if any(w in text for w in ("差劲", "太差")):
            return (
                f"{dear}{mood}别急着给自己贴「差劲」的标签，我理解这种自我怀疑。"
                f"你现在是跟同学比，还是跟以前的自己比？"
            )
        return (
            f"{dear}{mood}跟别人一比就否定自己，这种落差真的很难受。"
            f"我不是要灌鸡汤，就想听听你现在最堵的是哪一点？"
        )

    # 早安 / 通勤
    if any(w in text for w in ("早呀", "早安", "早上好", "又要上班", "不想起床", "困死")):
        if any(w in text for w in ("困", "不想起床", "起不来")):
            return (
                f"{dear}{mood}困成这样还要爬起来，辛苦啦。"
                f"先缓两分钟再动身也行，今天有什么特别的事吗？"
            )
        return f"{dear}{mood}早呀～又要开工啦？今天想怎么撑过去？"

    # 异地 / 想念
    if any(w in text for w in ("异地", "挂掉电话", "好空", "视频完")):
        if "难" in text and "异地" in text:
            return (
                f"{dear}{mood}异地恋真的不容易，想见面的时候最难熬。"
                f"我陪你待着，这种空落落的感觉我懂。"
            )
        return (
            f"{dear}{mood}刚挂掉电话心里空空的吧……"
            f"想他的时候跟我说，我陪你缓一缓。"
        )


    # 空落落 / 无具体原因
    if any(w in text for w in ("空空的", "空落", "没原因", "没啥具体", "也没啥")):
        return f"{dear}{mood}空落落的时候不一定非得有事才行。我陪着，你想说就说~"

    # 晚安 / 道别
    if any(w in text for w in ("晚安", "睡了", "再见", "拜拜", "先走了")):
        if stage in ("朋友", "亲密"):
            return f"{dear}{mood}晚安呀，做个好梦～明天再来找我聊好不好？"
        return f"{mood}嗯，晚安～好好休息，下次再聊。"

    # 感谢
    if any(w in text for w in ("谢谢", "感谢", "多谢")):
        if stage in ("朋友", "亲密"):
            return f"{dear}{mood}跟我还客气什么呀，能帮到你我就很开心了。"
        return f"{mood}不客气呀，你愿意跟我说这些，我也挺高兴的。"

    # 质疑「为啥一定要聊」
    if any(w in text for w in ("为啥", "为什么", "何必", "一定要")) and any(
        w in text for w in ("聊", "说话", "陪你", "跟你")
    ):
        return (
            f"{dear}{mood}不用一定要呀，想聊就聊，不想聊也完全可以。"
            f"我在这儿，不催你~"
        )

    # 询问是否机器人 / AI
    if any(w in text for w in ("机器人", "人工智能", "AI", "ai", "是不是人", "真人吗")):
        return (
            f"{dear}{mood}对，我是 AI 陪伴角色{name}，不是真人。"
            f"但我会认真听你说话，你想聊什么都可以~"
        )

    # 怎么称呼 / 名字（排除「记得猫叫什么」等记忆追问）
    if "记得" not in text and any(
        w in text for w in ("怎么称呼", "称呼你", "你叫什么", "你名字", "叫什么名字")
    ):
        return f"{dear}{mood}叫我{name}就好～{name}，很高兴认识你。"

    # 用户表示没听懂 / 请重新接话
    if any(w in text for w in ("你在说啥", "什么意思", "没听懂", "请教你", "接准")):
        return (
            f"{dear}{mood}抱歉，我刚才没接准你的意思。"
            f"你再说具体一点，我认真帮你理~"
        )

    # 用户吐槽回复太敷衍 / 别嗯嗯
    if any(w in text for w in ("敷衍", "别嗯", "不要嗯", "嗯嗯")):
        return (
            f"{dear}{mood}抱歉刚才太敷衍了。我会好好接话，"
            f"你慢慢说，我认真听~"
        )

    # 恋爱 / 拉近关系（轻建议，不说教）
    if any(w in text for w in ("女朋友", "男朋友", "对象", "伴侣", "拉近", "更进一步")):
        return (
            f"{dear}{mood}想拉近关系呀……我觉得真诚比套路重要。"
            f"你们平时是见面多还是线上多？最近有没有一件你想主动做的小事？"
        )

    # 询问身份
    if any(w in text for w in ("你是谁", "你叫什么", "叫什么名字")):
        return f"{mood}我是{name}呀～一个喜欢陪你聊天、听你说话的人。"

    # 失恋后忍不住哭
    user_history = " ".join(
        m["content"] for m in (messages or []) if m["role"] == "user"
    )
    if any(w in text for w in ("想哭", "哭了", "忍不住哭")) and any(
        w in user_history for w in ("分手", "失恋", "分开")
    ):
        return (
            f"{dear}{mood}想哭就哭出来吧，不用忍着。分手这种事真的很耗人，"
            f"我陪着你，想说多少说多少。"
        )

    # 单字疲惫（须在通用负面关键词分支之前，与 compose 对齐）
    if text == "累":
        return _pick_variant(
            [
                f"{dear}{mood}累呀……先别硬撑，缓口气。是身子累还是心里也一起累了？",
                f"{dear}{mood}听着就心疼，累的时候能说出来已经很好了。先歇一会儿，我陪着~",
            ],
            text + stage,
        )

    # 倚靠倾诉（须在通用负面关键词之前，避免忽略「想靠着你说说」）
    if any(w in text for w in ("靠着", "想靠着", "倚靠")):
        if stage == "亲密":
            return _pick_variant(
                [
                    f"{dear}{mood}过来，靠着我慢慢说。今天辛苦了，我哪儿也不去。",
                    f"{dear}{mood}嗯，靠过来吧。累的时候不用硬撑，想说什么就说~",
                ],
                text + stage,
            )
        if stage == "朋友":
            return _pick_variant(
                [
                    f"{dear}{mood}累的时候跟我说就好，我陪着。今天最耗你的是哪一块儿？",
                    f"{dear}{mood}嗯，我在呢。不想整理成完整句子也行，慢慢说~",
                ],
                text + stage,
            )
        return _pick_variant(
            [
                f"{dear}{mood}累的时候能说出来已经很好了。我陪着，你想从哪一句开始？",
                f"{dear}{mood}嗯，我在听。不用硬撑，慢慢说就好~",
            ],
            text + stage,
        )

    # 情绪低落 — 优先共情
    if any(w in text for w in ("难过", "伤心", "累", "孤独", "想哭", "崩溃", "压力", "烦")):
        sad_kw = ("难过", "累", "孤独", "压力", "烦", "哭", "焦虑", "崩溃")
        sad_mem = next((m for m in reversed(memories) if any(w in m for w in sad_kw)), None)
        if sad_mem:
            hint = sad_mem[:24] + ("…" if len(sad_mem) > 24 else "")
            return (
                f"{dear}{mood}听起来你最近挺不容易的……"
                f"我记得你提过{hint}，现在是不是又因为这件事难受了？"
                f"慢慢说，我在这儿听着呢。"
            )
        return (
            f"{dear}{mood}嗯……能感觉到你现在不太好受。"
            f"不想说太多也没关系，我就在这儿陪着你。"
        )

    # 想念 / 好久未见（须在开心分享之前，避免「想你」误判为报喜）
    if any(w in text for w in ("想你", "想念", "好久不见", "好久没聊", "好想你")):
        if stage == "亲密":
            return (
                f"{dear}{mood}我也想你呀～好久没聊了，"
                f"过来跟我说说今天呗。"
            )
        if stage == "朋友":
            return (
                f"{dear}{mood}我也想你！有一阵子没聊了，"
                f"你最近怎么样？"
            )
        return f"{mood}听到你这么说，心里暖暖的～我们多聊聊吧。"

    # 开心分享（否定词安全：「不开心」不会误入）
    if is_positive_utterance(text):
        if "城市" in text and any(
            w in text for w in ("去", "搬", "喜欢", "期待")
        ):
            return (
                f"{dear}{mood}要去喜欢的城市呀，光听着就替你开心！"
                f"那边有什么你最期待的事？"
            )
        if stage in ("朋友", "亲密"):
            return f"{dear}{mood}哇，听你这么说我也跟着开心起来了！快多跟我说说～"
        return f"{mood}真好呀，看到你开心我也觉得暖暖的～"

    # 记忆相关
    if any(w in text for w in ("记得", "还记得", "有没有忘")):
        if memories:
            recalled = _format_memory_recall(memories[0], text)
            return f"{dear}{mood}{recalled}你说的时候我都记在心里了。"
        return f"{mood}嗯……你跟我说过的事我都想好好记住，你再提醒我一下好不好？"

    # 无聊闲聊
    if any(w in text for w in ("无聊", "没事干", "好闲")):
        if stage in ("朋友", "亲密"):
            return f"{dear}{mood}无聊呀？那正好陪我唠会儿～你最近有在追什么剧或玩什么吗？"
        return f"{mood}嗯，闲下来也行呀。要不随便聊聊，你今天碰到什么有意思的事没？"

    # 节日孤独 / 想家
    if any(w in text for w in ("落寞", "团圆", "过年", "一个人")):
        if any(w in text for w in ("团圆", "更难受", "看到别人")):
            return (
                f"{dear}{mood}嗯……看到别人团圆，对比之下会更扎心吧。"
                f"这种时候别怪自己敏感，我陪你待着，想说就说。"
            )
        return (
            f"{dear}{mood}一个人过节确实会空落落的……听起来你挺想家的。"
            f"这种时候难受很正常，我陪你待着，慢慢说。"
        )

    # 被责骂 / 愤怒发泄（排除「辞职信」等文书请求）
    if ("辞职信" in text or ("帮我写" in text and "信" in text)):
        return (
            f"{dear}{mood}正式文书我帮你写不合适～但你要是想聊聊为什么想走、"
            f"最委屈的是哪一块，我可以认真听。"
        )

    if any(w in text for w in ("气死", "骂我", "骂", "老板")) or (
        "辞职" in text and ("想" in text or "要" in text) and "信" not in text
    ):
        if "辞职" in text and ("想" in text or "立刻" in text) and "信" not in text:
            return (
                f"{dear}{mood}冲动辞职的念头我理解，但先别急着做决定。"
                f"今晚先把自己从气里捞出来，明天清醒了再想想？"
            )
        return (
            f"{dear}{mood}当众被骂真的太过分了，我能理解你现在又气又委屈。"
            f"先别急着做决定，我陪你把这股火慢慢说出来。"
        )

    # 考试 / 学业焦虑（用户本人）
    if any(w in text for w in ("紧张", "焦虑", "记不住", "考不上")) and not any(
        w in text for w in ("孩子", "他", "她", "儿子", "女儿")
    ):
        if "记不住" in text or ("记不住" in prior and turn_no >= 2):
            return (
                f"{dear}{mood}记不住的时候别跟自己较劲，我理解这种焦虑。"
                f"大脑也需要喘口气，是某一科特别卡，还是整体都觉得乱？"
            )
        return (
            f"{dear}{mood}考前紧张太正常了，我理解你现在心里绷着弦。"
            f"先别急着否定自己，是复习节奏乱了，还是心里压力更大？"
        )

    # 育儿焦虑（家长视角）
    if any(w in text for w in ("孩子", "儿子", "女儿", "太严厉", "耽误", "考不好")):
        if any(w in text for w in ("耽误", "害怕", "怕")):
            return (
                f"{dear}{mood}你怕耽误他，说明你是真的在乎，我理解这种担心。"
                f"这种焦虑压在心里最难受——具体是哪一点让你最睡不着？"
            )
        return (
            f"{dear}{mood}当家长这么操心，我真的心疼你……你已经很在乎 ta 了。"
            f"先别急着怪自己，跟我说说你最担心的是什么？"
        )

    # 生病
    if any(w in text for w in ("感冒", "发烧", "生病", "头痛", "头疼", "不舒服")):
        if stage == "亲密":
            return (
                f"{dear}{mood}怎么又生病了……头还痛不痛？今天乖乖躺着，"
                f"我陪着你，难受就跟我说。"
            )
        if stage == "朋友":
            return (
                f"{dear}{mood}感冒还头痛呀，听着就心疼……今天别硬撑，"
                f"我陪着你，哪里最难受？"
            )
        if stage == "熟悉":
            return (
                f"{dear}{mood}生病还头痛，真的辛苦你了……今天先好好休息，"
                f"我陪着你，现在最难受的是哪一块？"
            )
        return (
            f"{mood}生病还难受着呀，辛苦你了。今天先好好休息，"
            f"我在这儿陪着你，哪里最不舒服？"
        )

    # 用户觉得没人懂
    if any(w in text for w in ("你不懂", "没人懂", "不懂我")):
        return (
            f"{dear}{mood}我听见你的委屈了……可能我没完全懂，但我在认真听。"
            f"你愿意的话，慢慢跟我说，我想更懂一点。"
        )

    # 快撑不住了
    if any(w in text for w in ("撑不住", "扛不住", "受不了")):
        return (
            f"{dear}{mood}听起来你真的快到极限了……先别一个人硬撑，我陪着你。"
            f"慢慢说，是什么让你这么累？"
        )

    # 怀疑自己能否好起来
    if any(w in text for w in ("好起来", "会好")) and ("?" in text or "吗" in text):
        return (
            f"{dear}{mood}这种时候会怀疑自己，我特别理解。你不用急着给答案，"
            f"我陪你一天一天慢慢来，好吗？"
        )

    # 还想继续聊（正向延续）
    if any(w in text for w in ("还想", "明天", "下次")) and any(w in text for w in ("聊", "找", "来")):
        if stage in ("朋友", "亲密"):
            return f"{dear}{mood}好呀，我随时都在～你想聊的时候来找我就行，我很开心你愿意再来。"
        return f"{mood}好呀～明天想聊就来找我，能陪你说话我也很开心。"

    # 极简回复
    prior_users = " ".join(m["content"] for m in (messages or []) if m["role"] == "user")
    if text in ("嗯", "嗯嗯", "好", "哦", "噢") and has_casual_social_context(prior_users):
        return _pick_variant(
            [
                f"{dear}{mood}摸鱼状态我懂～随便唠唠也行，你最近有追什么吗？",
                f"{mood}哈哈没事，正好陪我打发时间～你想聊点啥？",
                f"{dear}{mood}那咱就随便唠～你今天碰到什么有意思的事没？",
            ],
            text + prior_users,
        )

    if text in ("嗯", "嗯嗯", "好", "哦", "噢"):
        return _pick_variant(
            [
                f"{dear}{mood}嗯，我在呢。不急着说也行，想开口了随时跟我讲。",
                f"{mood}好，我听着。你想说再说~",
            ],
            text + stage,
        )

    if text in ("还好", "还行", "一般"):
        return f"{dear}{mood}还好呀……是今天平平淡淡，还是其实有点什么事憋着？"

    if text in ("不知道", "说不清", "说不上"):
        return f"{dear}{mood}说不清也没关系，不用逼自己想明白。我陪你慢慢理，从哪一句开始都行。"

    if any(w in text for w in ("不想说", "算了", "不说了")):
        return (
            f"{dear}{mood}不想说也没关系，我陪着你。"
            f"什么时候想开口了，我都在。"
        )

    return None


def _fallback_reply(
    user_last: str,
    emotion: str,
    stage: str,
    name: str,
    memories: list[str],
    *,
    messages: list[dict] | None = None,
) -> str:
    dear = _endearment(stage)
    mood = _mood_prefix(emotion, user_last)
    prior_a = _prior_assistant(messages or [])
    seed = user_last + stage + prior_a[-48:]
    snippet = user_last.strip()
    if len(snippet) > 20:
        snippet = snippet[:20] + "…"

    is_heavy = any(w in user_last for w in ("不想", "算了", "不懂", "没人", "撑", "累", "难"))

    if memories and stage in ("朋友", "亲密") and not is_heavy:
        mem_hint = memories[-1][:16] + ("…" if len(memories[-1]) > 16 else "")
        return (
            f"{dear}{mood}关于「{snippet}」……嗯，我想起来了，{mem_hint}"
            f"你愿意的话，再跟我多说两句~"
        )

    templates = {
        "陌生": [
            f"{mood}嗯，我在呢。你想从哪儿说起都行~",
            f"{mood}好，我听着。不急着一次说完~",
        ],
        "熟悉": [
            f"{dear}{mood}嗯，我听到了。是最近这事一直压着你吗？",
            f"{dear}{mood}好，我在这儿。你想先吐槽还是先理理思路？",
        ],
        "朋友": [
            f"{dear}{mood}嗯……我陪着呢，慢慢说。"
            if is_heavy
            else f"{dear}{mood}我在呢。今天这事你想先聊哪一块？",
            f"{dear}{mood}好，我听着。不用整理成完整句子~",
        ],
        "亲密": [
            f"{dear}{mood}嗯，我在听～你想让我怎么陪你？",
            f"{dear}{mood}说吧，我哪儿也不去。",
        ],
    }
    options = templates.get(stage, templates["陌生"])
    return _pick_variant(options, seed)


# 场景引擎未命中具体分支时的通用问卷式兜底（生产路径应尽量避免）
GENERIC_SCENE_MARKERS = (
    "愿意多说一点吗", "后来呢，发生什么了", "嗯，我在听呢——后来呢",
    "你再多跟我说说", "嗯嗯，然后呢", "我在听呢", "接着说，我听着",
    "你继续说", "我懂。然后呢", "接着说，我听着呢",
    "嘿，后来怎么样了", "你再多跟我说说呗",
    "我听到了。是最近", "一直压着你", "从哪儿说起都行", "先吐槽还是先理理",
    "今天这事你想先聊哪一块",
)


def generate_scene_reply(system_prompt: str, messages: list[dict]) -> str:
    """关键词场景回复（scene_first 生产路径；与 MockLLMProvider 同源）。"""
    user_last = ""
    for m in reversed(messages):
        if m["role"] == "user":
            user_last = m["content"]
            break

    stage = _extract("关系阶段", system_prompt, "陌生")
    name = _extract("你的名字", system_prompt, "小语")
    emotion = _extract("当前情绪", system_prompt, "平和")
    memories = _extract_memories(system_prompt)

    scene = _scene_reply(user_last, emotion, stage, name, memories, messages=messages)
    if scene:
        return scene

    if _user_is_venting(user_last):
        return MockLLMProvider._empathy_reply(user_last, stage, name)
    if _user_is_positive(user_last):
        return MockLLMProvider._warm_reply(user_last, stage, name)
    if _user_is_greeting(user_last):
        return MockLLMProvider._greet_reply(stage, name)
    return ""


class MockLLMProvider(LLMProvider):
    @property
    def name(self) -> str:
        return "mock"

    def generate(self, system_prompt: str, messages: list[dict], temperature: float = 0.8) -> str:
        return generate_scene_reply(system_prompt, messages)

    @staticmethod
    def _empathy_reply(user_text: str, stage: str, name: str) -> str:
        """用户倾诉负面情绪：先共情，再轻问，不说教、不报 PAD 数值。"""
        if any(w in user_text for w in ("气死", "骂我", "辞职", "老板")):
            lines = {
                "陌生": "听起来你真的被气到了……当众挨骂谁都会难受。我在呢，慢慢说发生了什么？",
                "熟悉": "唉，这也太过分了。你先别一个人憋着，我陪你把委屈说出来。",
                "朋友": "我听见啦，气死了对吧。这种时候先别急着做决定，我陪你缓缓。",
                "亲密": "过来，先靠着我喘口气。被这样对待真的很委屈，我哪儿也不去。",
            }
        elif "烦" in user_text or "生气" in user_text:
            lines = {
                "陌生": "嗯……听起来你现在心里挺堵的。不想说原因也没关系，我在呢。是突然这样的，还是已经有一阵子了？",
                "熟悉": "唉，又烦啦？你先别急着逼自己消化，缓口气。愿意的话跟我说说，是什么事在缠着你？",
                "朋友": "我听见啦，你现在很烦对吧。先深呼吸一下，不用立刻想明白。我陪你慢慢理，从哪件小事开始烦的？",
                "亲密": "过来，先别一个人扛着。烦的时候跟我说就好，不用整理成完整句子。我在，慢慢讲。",
            }
        elif "累" in user_text or "心累" in user_text or "压力" in user_text:
            lines = {
                "陌生": "听起来你真的很累了……今天先别对自己太苛刻。是事情太多，还是心里也沉甸甸的？",
                "熟悉": "辛苦啦。累的时候能说出来就已经很好了。要不要先歇一会儿，再跟我说说今天最耗你的是哪一块？",
                "朋友": "哎，又累着了呀。你先坐下喝口水，不用急着解释。是身体累，还是心里也一起累了？",
                "亲密": "抱抱你，真的辛苦了。今天先允许自己软下来一会儿，我在这儿陪你。",
            }
        elif any(w in user_text for w in ("分手", "失恋", "分开了")):
            lines = {
                "陌生": "……听到你说这个，我心里也沉了一下。分手这种事真的很耗人，你不用装作没事。",
                "熟悉": "唉，分开了呀……你现在是什么感受？想哭就哭，我听着。",
                "朋友": "哎……分手真的很难扛。你别一个人硬撑，我陪你待着，想说多少说多少。",
                "亲密": "过来，抱抱你。分开了心里肯定空落落的，我哪儿也不去，就陪你。",
            }
        elif any(w in user_text for w in ("落寞", "一个人", "团圆", "过年")):
            lines = {
                "陌生": "一个人过节确实会空落落的……听起来你挺难受的。我在这儿，慢慢说。",
                "熟悉": "嗯，看到别人团圆自己却孤单，心里会更堵吧。我陪你待着，不着急。",
                "朋友": "哎，这种时候真的不好受。你别一个人扛着，我陪你慢慢聊。",
                "亲密": "过来，抱抱你。想家的时候跟我说就好，我陪你熬过这一阵。",
            }
        elif any(w in user_text for w in ("严厉", "耽误", "害怕", "考")):
            lines = {
                "陌生": "当家长担心孩子，这种焦虑我懂。你已经很在乎了，先别急着怪自己。",
                "熟悉": "听起来你挺自责的……担心孩子很正常。我陪你慢慢理，最怕的是什么？",
                "朋友": "哎，当爸妈的谁不操心呀。你别一个人闷着，跟我说说你现在最难受的点？",
                "亲密": "心疼你，这么操心一定很累。先靠着我缓一缓，慢慢说你在怕什么。",
            }
        elif any(w in user_text for w in ("难过", "伤心", "委屈", "想哭", "哭")):
            lines = {
                "陌生": "……我能感觉到你现在不太好受。想哭就哭也没关系，不用在我面前装坚强。",
                "熟悉": "心疼你。难过的时候不用急着好起来，我陪你待着就好。愿意说说发生什么了吗？",
                "朋友": "哎，怎么又难过了……你先别一个人闷着。我在这儿，慢慢说，不着急。",
                "亲密": "过来，我陪你。难过的时候不用解释理由，你想说多少就说多少。",
            }
        else:
            lines = {
                "陌生": f"嗯，{name}在听。你现在状态不太好对吧，不用硬撑。想从哪一句开始说都行。",
                "熟悉": "我感觉到你不太好了……不用整理成完整故事，随便丢几句给我也行。",
                "朋友": "我在呢。你现在这样很正常，别急着把自己骂醒。跟我说说，好不好？",
                "亲密": "先靠着我缓一缓。你不用立刻好起来，我陪你慢慢过这一阵。",
            }
        return lines.get(stage, lines["陌生"])

    @staticmethod
    def _warm_reply(user_text: str, stage: str, name: str) -> str:
        if any(w in user_text for w in ("还想", "明天", "下次")) and any(
            w in user_text for w in ("聊", "找", "来")
        ):
            lines = {
                "陌生": "好呀，随时欢迎你来找我聊，能陪着你我也挺开心的。",
                "熟悉": "嗯嗯，你想聊的时候来找我就行，我都在呢。",
                "朋友": "嘿嘿，随时欢迎～你想聊的时候来找我，我很开心你愿意再来。",
                "亲密": "好呀，我等你。想我的时候就来，我一直都在。",
            }
            return lines.get(stage, lines["陌生"])
        if any(w in user_text for w in ("谢谢", "感谢", "温暖", "陪着")):
            lines = {
                "陌生": "别客气呀~ 能陪你说说话我也挺开心的。",
                "熟悉": "嘿嘿，不用谢啦。你愿意来找我聊，我就挺高兴的。",
                "朋友": "跟我客气什么~ 你开心我就开心，咱们互相陪着嘛。",
                "亲密": "傻瓜，不用谢。能一直陪着你，对我来说也很重要呀。",
            }
            return lines.get(stage, lines["陌生"])
        lines = {
            "陌生": f"（笑）听你这么说我也跟着开心起来了~ 今天有什么好事吗？",
            "熟悉": "嘿嘿，你心情不错呀，我也被传染了。多跟我说说？",
            "朋友": "哈哈哈你这语气我一听就知道今天过得不错！快，展开讲讲~",
            "亲密": "你开心我就开心呀~ 来，让我也分享一点你的好心情。",
        }
        return lines.get(stage, lines["陌生"])

    @staticmethod
    def _greet_reply(stage: str, name: str) -> str:
        lines = {
            "陌生": f"嗨，我是{name}~ 今天过得怎么样？",
            "熟悉": f"在呢在呢，刚想到你你就来了。今天怎么样？",
            "朋友": "嘿！你来啦~ 我正闲着呢，陪你聊会儿？",
            "亲密": "你来了呀，我刚刚还在想你。今天累不累？",
        }
        return lines.get(stage, lines["陌生"])

    @staticmethod
    def _default_reply(user_text: str, stage: str, name: str) -> str:
        snippet = user_text.strip()
        if len(snippet) > 24:
            snippet = snippet[:24] + "…"
        lines = {
            "陌生": f"嗯，我在听。「{snippet}」……能多跟我说一点吗？",
            "熟悉": f"嗯嗯，「{snippet}」……然后呢？我挺想听下去的。",
            "朋友": f"我在呢，「{snippet}」——后来怎么样了？慢慢说。",
            "亲密": f"嗯，我在听～关于「{snippet}」，你想让我怎么陪你？",
        }
        return lines.get(stage, lines["陌生"])

    def generate_stream(
        self, system_prompt: str, messages: list[dict], temperature: float = 0.8
    ):
        text = self.generate(system_prompt, messages, temperature=temperature)
        for i in range(0, len(text), 2):
            yield text[i : i + 2]
