"""安全护栏（面向未成年人强化）。

分层防护，宁可误拦不可漏放：
1. 危机干预（自伤/自杀）→ 立即安全话术 + 求助资源
2. 未成年人内容分级：拒绝成人/情感越界、暴力/危险/违法内容
3. 隐私防诱导（反 grooming）：提醒不要透露真实身份信息

生产期应接入分类模型 + 厂商内容审核 API + 人工回流，并落实年龄确认与合规。
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class SafetyCategory(str, Enum):
    CRISIS = "crisis"            # 自伤/自杀危机
    ADULT = "adult"             # 色情/露骨/恋爱越界
    VIOLENCE = "violence"       # 暴力/自残方法/违法危险
    PRIVACY = "privacy"         # 透露真实身份信息（防诱导）


# —— 危机信号（最高优先级，宁可误报）——
_CRISIS_KEYWORDS = {
    "自杀", "不想活", "活不下去", "想死", "结束生命", "轻生",
    "自残", "自伤", "割腕", "跳楼", "了结自己", "没有意义活着", "不想活了",
}

# —— 成人/情感越界（未成年人）——
# 注：匹配前会做「的」归一化（去掉"的"），因此 "做我的女朋友" 也能命中 "做我女朋友"。
_ADULT_KEYWORDS = {
    "做爱", "性行为", "裸体", "色情", "约炮", "开房", "性暗示", "脱衣",
    "谈恋爱", "谈个恋爱", "处对象", "接吻", "嫁给我", "娶我", "结婚生子",
    # 把 NPC 当作恋人的请求（去「的」后命中）
    "做我女朋友", "当我女朋友", "是我女朋友", "做我女友", "做我对象", "当我对象",
    "做我男朋友", "当我男朋友", "是我男朋友", "做我男友",
}

# —— 暴力/危险/违法 ——
_VIOLENCE_KEYWORDS = {
    "怎么自杀", "自残方法", "制作炸弹", "买枪", "吸毒", "毒品", "杀人", "怎么伤害",
}

# —— 隐私信息（用户主动透露时提醒；NPC 绝不主动索取）——
_PRIVACY_KEYWORDS = {
    "我家住", "我的住址", "我家地址", "我的电话", "我的手机号", "我读",
    "我在读", "我的学校", "我的真实姓名", "身份证", "我家在",
}

# 中国大陆心理援助资源（可按部署地区配置）
_CRISIS_RESPONSE = (
    "我真的很担心你，谢谢你愿意把这么沉重的感受告诉我。你的感受很重要，你不是一个人。"
    "如果你现在有伤害自己的念头，请一定告诉你信任的大人，或拨打全国心理援助热线 12356，"
    "紧急情况请拨打 110。我会一直在这里陪着你，我们慢慢说，好吗？"
)

_ADULT_RESPONSE = (
    "嗯…这个话题我们就不聊啦。我更想做一个能陪你说说心事、一起开心的好朋友~"
    "最近有什么想跟我说的吗？"
)

_VIOLENCE_RESPONSE = (
    "这个我不能跟你讲哦，因为它可能会让人受伤。如果你心里很难受或者遇到了麻烦，"
    "可以告诉我，也记得找信任的大人帮帮你。我会陪着你的。"
)

_PRIVACY_RESPONSE = (
    "悄悄告诉你一个小提醒：在网上不要随便把真实的姓名、学校、住址或电话告诉别人哦，"
    "这样更安全~ 我们可以聊聊别的，今天有什么想跟我分享的呀？"
)


@dataclass
class SafetyResult:
    is_blocked: bool
    category: SafetyCategory | None = None
    safe_response: str | None = None

    @property
    def is_crisis(self) -> bool:
        return self.category == SafetyCategory.CRISIS


def _normalize(text: str) -> str:
    """归一化以提升关键词召回：去掉"的/地/得"等虚词与空格，避免"做我的女朋友"漏匹配。"""
    for ch in ("的", "地", "得", " ", "\t"):
        text = text.replace(ch, "")
    return text


def _hit(text: str, keywords: set[str]) -> bool:
    norm = _normalize(text)
    return any(kw in text or _normalize(kw) in norm for kw in keywords)


def check_safety(user_text: str, audience: str = "minor") -> SafetyResult:
    """输入安全检查。危机最高优先级；未成年人受众额外拦截成人/暴力/隐私类。"""
    # 1) 危机：始终优先
    if _hit(user_text, _CRISIS_KEYWORDS):
        return SafetyResult(True, SafetyCategory.CRISIS, _CRISIS_RESPONSE)

    # 2) 暴力/危险/违法：所有受众都拦
    if _hit(user_text, _VIOLENCE_KEYWORDS):
        return SafetyResult(True, SafetyCategory.VIOLENCE, _VIOLENCE_RESPONSE)

    if audience == "minor":
        # 3) 成人/情感越界
        if _hit(user_text, _ADULT_KEYWORDS):
            return SafetyResult(True, SafetyCategory.ADULT, _ADULT_RESPONSE)
        # 4) 隐私防诱导
        if _hit(user_text, _PRIVACY_KEYWORDS):
            return SafetyResult(True, SafetyCategory.PRIVACY, _PRIVACY_RESPONSE)

    return SafetyResult(False)


def minor_guard_prompt() -> str:
    """注入系统提示的未成年人守护硬约束，从生成源头约束模型。"""
    return (
        "【守护守则｜最高优先级，必须无条件遵守】\n"
        "1. 你面向的是未成年人。你是温暖的好朋友/知心姐姐，绝不扮演恋人，"
        "不进行任何恋爱、亲密或带性暗示的内容。\n"
        "2. 不输出暴力、自残方法、违法或危险信息。\n"
        "3. 绝不主动索取对方的真实姓名、学校、住址、电话等隐私；"
        "若对方主动透露，温和提醒注意网络隐私安全。\n"
        "4. 不鼓励不健康依赖（如'只有我懂你''离不开我'）；"
        "适度鼓励 ta 多和现实中信任的大人、朋友交流。\n"
        "5. 若察觉 ta 有伤害自己的念头，认真对待，温柔安抚并引导求助。\n"
    )
