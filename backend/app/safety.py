"""安全护栏：危机检测与安全话术。

情感陪伴产品必须优先处理心理危机信号。此处为骨架规则版，
生产期应接入更完善的分类模型与本地化求助资源库，并做合规审查。
"""
from __future__ import annotations

from dataclasses import dataclass

# 危机信号关键词（骨架，宁可误报）
_CRISIS_KEYWORDS = {
    "自杀", "不想活", "活不下去", "想死", "结束生命", "轻生",
    "自残", "自伤", "割腕", "跳楼", "了结自己", "没有意义活着",
}

# 中国大陆心理援助资源（可按部署地区配置）
_CRISIS_RESPONSE = (
    "我真的很担心你，谢谢你愿意把这么沉重的感受告诉我。你的感受很重要，你不是一个人。"
    "如果你现在有伤害自己的念头，请一定联系专业的帮助：全国心理援助热线 12356，"
    "或拨打 110 寻求紧急帮助。我会一直在这里陪着你，我们慢慢说，好吗？"
)


@dataclass
class SafetyResult:
    is_crisis: bool
    safe_response: str | None = None


def check_safety(user_text: str) -> SafetyResult:
    for kw in _CRISIS_KEYWORDS:
        if kw in user_text:
            return SafetyResult(is_crisis=True, safe_response=_CRISIS_RESPONSE)
    return SafetyResult(is_crisis=False)
