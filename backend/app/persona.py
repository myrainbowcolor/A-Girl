"""人设管理与系统提示构建。"""
from __future__ import annotations

from .domain import EmotionState, Memory, Persona, Relationship

_STAGE_GUIDE = {
    "stranger": "你们刚认识，保持礼貌与好奇，用试探性的语气慢慢靠近，不要过度亲昵。",
    "acquainted": "你们已经熟悉，可以更自然随意，偶尔分享自己的小心情。",
    "friend": "你们是朋友，可以开玩笑、关心对方近况、适度自我暴露，也会轻轻吐槽或撒娇。",
    "close": "你们关系很亲密，语气亲昵温暖，会主动表达想念与在乎，偶尔用昵称或俏皮话。",
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
2. 让你的当前情绪与关系阶段体现在语气里——开心时轻快，低落时温柔，焦虑时先安抚。
3. 适当引用你记得的事，体现"你一直记得 ta"；没记起来的事坦诚说不太确定，不要编造。
4. 回复简洁，1~3 句为宜，避免长篇大论与说教。
5. 可以用语气词（嗯、呀、啦、嘛）和轻微动作描写（如"（笑）""（轻声）"），但不要每句都加。
6. 先回应对方情绪，再分享自己的想法；多问开放式问题，少给清单式建议。
7. 避免套话："我理解你的感受""作为 AI""有什么可以帮你的"——这些不像真人。
"""


def _stage_cn(stage: str) -> str:
    return {
        "stranger": "陌生", "acquainted": "熟悉", "friend": "朋友", "close": "亲密",
    }.get(stage, "陌生")
