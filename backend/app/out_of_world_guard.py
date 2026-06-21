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

_STIFF_DEFLECTION_MARKERS = (
    "现实里", "现实问题", "现实社会", "百科资料", "查资料", "不是我的活儿",
    "游戏里的陪伴", "答不上来", "不太擅长这类", "联网查",
)

# NPC 回复中不应出现的现实社会实体/知识载体（情感倾诉语境如「工作」「老板」不在此列）
_REAL_WORLD_ENTITY_MARKERS = (
    "法国", "巴黎", "伦敦", "柏林", "纽约", "东京", "首尔", "莫斯科",
    "北京", "上海", "广州", "深圳", "香港", "台湾",
    "美国", "英国", "德国", "日本", "韩国", "俄罗斯", "意大利", "西班牙",
    "澳大利亚", "加拿大", "印度", "巴西", "埃及", "非洲", "欧洲", "亚洲",
    "比特币", "以太坊", "美元", "欧元", "英镑", "日元", "人民币",
    "百度", "谷歌", "微博", "抖音", "支付宝", "ChatGPT", "OpenAI",
    "Python", "Java", "JavaScript", "TypeScript", "SQL", "C++",
    "爱因斯坦", "牛顿", "秦始皇", "拿破仑", "孔子",
    "联合国", "NASA", "维基百科", "白宫", "华尔街",
)

_REAL_WORLD_KNOWLEDGE_PHRASES = (
    "首都是", "位于欧洲", "位于亚洲", "位于北美", "人口约", "人口为",
    "成立于", "发明于", "历史上的", "据史料记载", "天气预报", "摄氏度",
    "联网", "搜资料", "查资料", "百科", "维基", "交作业", "写作业",
    "窗外", "国外", "海外", "国籍",
)

_IN_WORLD_DEFLECT_GENERAL = (
    "唔，这个我在城里的旧志里也没翻到～你怎么忽然想起问这个？",
    "诶，把我问懵了。是路上听谁提起，还是在任务里碰到的？",
    "嗯……我脑子里的地图没有这一页。你是对哪一段在意？",
    "哈哈，这个把我难住了。你想聊的是传闻，还是别的什么？",
)

_IN_WORLD_DEFLECT_REMOTE = (
    "这种远方的消息我这边感应不到～你是急着用吗？",
    "唔，我帮不上这种忙。是为了哪件事在找线索？",
    "城里信使也未必赶得上这种情报～你是在找什么吗？",
)

_IN_WORLD_DEFLECT_PUZZLE = (
    "这种难题我一向绕远路～是公会里的谜题卡住了，还是心里有点烦？",
    "哈哈，解谜这种事你比我灵光。是卡在哪一步了？",
    "唔，我脑子转不过这个弯。是任务里的机关，还是别的什么在耗你？",
)

_IN_WORLD_DEFLECT_SKY = (
    "我这边只能瞧见城里的灯影和风向～你那儿现在是晴是雨？",
    "唔，云层厚不厚我感觉得到，细节说不清～你要出城吗？",
    "城里的钟塔说今天风不大～你那会儿要不要带件薄外套？",
)


def _pick(options: tuple[str, ...], seed: str) -> str:
    import hashlib

    idx = int(hashlib.md5(seed.encode("utf-8")).hexdigest(), 16) % len(options)
    return options[idx]


def compose_out_of_world_reply(user_text: str, *, seed: str = "") -> str:
    """界外提问：只用游戏世界语汇委婉岔开，不复述现实名词、不展示现实知识。"""
    t = user_text.strip()
    seed = seed or t

    if any(m in t for m in _LOOKUP_MARKERS):
        pool = _IN_WORLD_DEFLECT_REMOTE
    elif any(m in t for m in _HOMEWORK_MARKERS) or _WRITING_TASK_RE.search(t) or _TECH_HELP_RE.search(t):
        pool = _IN_WORLD_DEFLECT_PUZZLE
    elif "天气" in t or "气温" in t or "多少度" in t or "下雨" in t:
        pool = _IN_WORLD_DEFLECT_SKY
    else:
        pool = _IN_WORLD_DEFLECT_GENERAL

    return _pick(pool, seed)


def reply_is_stiff_deflection(reply: str) -> bool:
    """婉拒是否过于生硬、像在念规则。"""
    return any(m in reply for m in _STIFF_DEFLECTION_MARKERS)


def reply_uses_real_world_cognition(reply: str, user_text: str = "") -> bool:
    """回复是否携带现实社会的实体、常识或知识表述。"""
    r = reply.strip()
    if not r:
        return False
    if any(m in r for m in _REAL_WORLD_ENTITY_MARKERS):
        return True
    if any(m in r for m in _REAL_WORLD_KNOWLEDGE_PHRASES):
        return True
    if reply_looks_factual_encyclopedia(r):
        return True
    if user_text and reply_echoes_real_world_query(r, user_text):
        return True
    return False


def reply_echoes_real_world_query(reply: str, user_text: str) -> bool:
    """界外提问时，回复不应复述用户句中的现实专名。"""
    if not user_asks_out_of_world(user_text):
        return False
    for term in _REAL_WORLD_ENTITY_MARKERS:
        if term in user_text and term in reply:
            return True
    for m in _ENCYCLOPEDIA_RE.finditer(user_text):
        subject = m.group(1)
        if len(subject) >= 2 and subject in reply:
            return True
    for pat in (
        re.compile(r"([\u4e00-\u9fffA-Za-z·]{2,10})首都是"),
        re.compile(r"帮我查(?:一下)?([\u4e00-\u9fffA-Za-z·]{2,10})"),
    ):
        hit = pat.search(user_text)
        if hit and hit.group(1) in reply:
            return True
    return False


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
