"""拦截现实百科/查资料/作业类越界提问，保持游戏陪伴体验。"""
from __future__ import annotations

import re

_LOOKUP_MARKERS = (
    "查一下", "帮我查", "搜一下", "搜索一下", "百度一下", "谷歌",
    "联网查", "百科", "维基", "维基百科", "帮我算", "计算一下", "算一下",
)

_HOMEWORK_MARKERS = (
    "解题", "答案是什么", "怎么做题", "帮我翻译", "翻译这段", "翻译一下",
)

_EMOTIONAL_COMPANION_MARKERS = (
    "累", "烦", "难过", "开心", "孤独", "焦虑", "委屈", "压力", "心累",
    "怎么办", "咋办", "不想", "觉得", "感觉", "我想", "我不想", "好烦",
    "好难过", "好热", "好冷", "睡不着", "失眠", "吵架", "分手", "加班",
    "老板", "工作", "考试", "女朋友", "男朋友", "陪我", "聊聊", "说说",
)

_COMPANION_WHAT_IS = (
    "意思", "陪伴", "朋友", "生活", "人生", "爱", "爱情", "你", "我", "我们",
)

_TECH_HELP_RE = re.compile(
    r"(代码|程序|函数|脚本|SQL|Python|Java|C\+\+).{0,12}(怎么|如何)(写|实现|配置|运行)|"
    r"(怎么|如何)(写|实现|配置).{0,8}(代码|程序|Python|Java|函数)"
)

_WRITING_TASK_RE = re.compile(r"(帮我写|代写).{0,8}(作文|论文|报告|方案|代码|脚本)")

_FACTUAL_Q_RES = (
    re.compile(r"首都是(哪|什么|哪里|哪儿)"),
    re.compile(r"(谁|哪个人|哪位)(发明|发现|创造|创立|写下)"),
    re.compile(r"哪[一]?年(成立|出生|发明|发生)"),
    re.compile(r"(人口|面积)有?(多少|多大|几)"),
    re.compile(r"(股价|汇率|比特币|基金|石油).{0,10}(多少|几|涨|跌|行情)"),
    re.compile(r"(今天|明天|后天|现在).{0,8}(天气|气温).{0,6}(怎么样|如何|多少度|吗|[?？]$)"),
    re.compile(r"(天气预报|多少度|会下雨吗|下不下雨)"),
    re.compile(r"第[\d一二三四五六七八九十百千]+[道题]"),
    re.compile(r"\d+\s*[+\-×÷*/]\s*\d+\s*(等于|是多少|得)"),
    re.compile(r"告诉我.{2,24}(首都|人口|面积|历史|资料)"),
)

_ENCYCLOPEDIA_RE = re.compile(
    r"([\u4e00-\u9fffA-Za-z·]{2,14})(是什么|是啥)([？?吗呢]|$)"
)

_FACTUAL_REPLY_MARKERS = (
    "首都是", "位于", "地处", "成立于", "创立于", "发明于", "被发现于",
    "人口约", "人口为", "面积为", "据我所知", "一般来说", "定义为",
    "指的是", "是世界上", "如下：", "如下:", "步骤如下", "方法如下",
)


def _has_emotional_companion_context(text: str) -> bool:
    return any(m in text for m in _EMOTIONAL_COMPANION_MARKERS)


def user_asks_out_of_world(user_text: str) -> bool:
    """用户是否在问现实百科/查资料/作业，而非情感陪伴。"""
    t = user_text.strip()
    if not t or len(t) < 4:
        return False

    from .reply_guard import user_is_identity, user_is_meta_pushback

    if user_is_identity(t) or user_is_meta_pushback(t):
        return False

    if "辞职信" in t or ("帮我写" in t and "信" in t):
        return False

    if any(m in t for m in _LOOKUP_MARKERS):
        return True
    if any(m in t for m in _HOMEWORK_MARKERS):
        return True
    if _WRITING_TASK_RE.search(t):
        return True
    if _TECH_HELP_RE.search(t):
        return True

    for pat in _FACTUAL_Q_RES:
        if pat.search(t):
            return True

    if ("天气" in t or "气温" in t) and any(
        w in t for w in ("怎么样", "如何", "多少度", "预报", "查")
    ):
        if not _has_emotional_companion_context(t):
            return True

    if "是什么" in t or "是啥" in t:
        if any(w in t for w in ("什么意思", "啥意思", "是什么意思")):
            return False
        m = _ENCYCLOPEDIA_RE.search(t)
        if m:
            subject = m.group(1)
            if any(w in subject for w in _COMPANION_WHAT_IS):
                return False
            if _has_emotional_companion_context(t):
                return False
            return True

    return False


def reply_looks_factual_encyclopedia(reply: str) -> bool:
    """回复是否在答现实百科/教程，而非陪伴。"""
    r = reply.strip()
    if len(r) < 12:
        return False
    hit = sum(1 for m in _FACTUAL_REPLY_MARKERS if m in r)
    if hit >= 2:
        return True
    if hit >= 1 and len(r) > 48:
        return True
    if re.search(r"\d{3,4}年.{0,12}(成立|发明|发生|出生)", r):
        return True
    if re.search(r"^[\d一二三四五六七八九十]+[、.．]", r) and len(r) > 40:
        return True
    return False
