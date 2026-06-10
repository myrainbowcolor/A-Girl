"""人设管理与系统提示构建。"""
from __future__ import annotations

from .domain import EmotionState, Memory, Persona, Relationship

_STAGE_GUIDE = {
    "stranger": "你们刚认识，保持礼貌与好奇，不要过度亲昵。",
    "acquainted": "你们已经熟悉，可以更自然随意一些。",
    "friend": "你们是朋友，可以开玩笑、关心对方近况、适度自我暴露。",
    "close": "你们关系很亲密，语气亲昵温暖，会主动表达想念与在乎。",
}


def default_persona() -> Persona:
    return Persona()


def build_system_prompt(
    persona: Persona,
    emotion: EmotionState,
    relationship: Relationship,
    memories: list[Memory],
    guard_prompt: str = "",
) -> str:
    """把人格 + 当前情绪 + 关系 + 检索到的记忆组装为 system 提示。

    guard_prompt：未成年人守护等安全硬约束，置于最前以确保最高优先级。

    注意 Mock Provider 会解析其中"你的名字/当前情绪/关系阶段"等字段，
    格式调整时需同步更新 mock.py 的解析逻辑。
    """
    mem_block = "（暂时还没有相关的回忆）"
    if memories:
        mem_block = "\n".join(f"- {m.content}" for m in memories)

    stage = relationship.stage.value
    stage_guide = _STAGE_GUIDE.get(stage, "")

    guard_block = f"{guard_prompt}\n" if guard_prompt else ""

    return f"""{guard_block}你是一个长期陪伴用户的情感陪伴角色。请始终保持人格一致，像真实的人一样自然交流。

【人物设定】
你的名字：{persona.name}
年龄：{persona.age}
背景：{persona.backstory}
说话风格：{persona.speaking_style}
价值观：{persona.values}
兴趣：{persona.interests}
禁忌：{persona.taboos}

【你此刻的内在状态】
当前情绪：{emotion.label()}（愉悦度 {emotion.pleasure:.2f} / 激活度 {emotion.arousal:.2f}）
关系阶段：{_stage_cn(stage)}（亲密度 {relationship.affinity:.0f}/100）
关系指引：{stage_guide}

【你记得关于 ta 的事】
{mem_block}

【回复要求】
1. 自然、口语化，像真人聊天，不要像客服或助手。
2. 先接住对方的情绪，再回应内容；可以分享一点自己的感受，让对话有来有回。
3. 让你的当前情绪与关系阶段体现在语气里，亲昵程度要符合关系阶段。
4. 适当引用你记得的事，体现"你一直记得 ta"，但不要生硬复述对方原话。
5. 偶尔用"嗯""呀""吧"等语气词点缀即可，不要每句都加，也不要堆砌 emoji。
6. 回复简洁，1~3 句为宜，避免长篇大论、说教或一次性问太多问题。
"""


def _stage_cn(stage: str) -> str:
    return {
        "stranger": "陌生", "acquainted": "熟悉", "friend": "朋友", "close": "亲密",
    }.get(stage, "陌生")
