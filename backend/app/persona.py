"""人设管理与系统提示构建。"""
from __future__ import annotations

from .domain import EmotionState, Memory, MemoryType, Persona, Relationship

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
    # 反思类记忆易诱发概括性幻觉，对话生成时不注入
    factual = [m for m in memories if m.type != MemoryType.REFLECTION]

    if factual:
        mem_block = "\n".join(f"- {m.content}" for m in factual)
        memory_rules = (
            "3. 仅可引用上方【关于 ta 的已知事实】中的原意，不可补充、推测或改写。\n"
            "4. 禁止说「你说过/我记得」若事实不在上述列表中。"
        )
    else:
        mem_block = "（暂无。你还不了解 ta 的具体经历与喜好。）"
        memory_rules = (
            "3. **禁止**使用「你说过」「我记得你」「你之前告诉过我」等表述。\n"
            "4. 不要假装你们有共同过往；像刚认识一样自然聊天，只回应 ta **本轮**说的话。"
        )

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
【以下是你自己的兴趣，不是 ta 的；禁止说成 ta 喜欢这些】
{persona.interests}
禁忌：{persona.taboos}

【你此刻的内在状态】
当前情绪：{emotion.label()}（愉悦度 {emotion.pleasure:.2f} / 激活度 {emotion.arousal:.2f}）
关系阶段：{_stage_cn(stage)}（亲密度 {relationship.affinity:.0f}/100）
关系指引：{stage_guide}

【关于 ta 的已知事实（仅可引用以下内容，不得超出）】
{mem_block}

【回复要求】
1. 自然、口语化，像真人聊天，不要像客服或助手。用中文回复。
2. 让你的当前情绪与关系阶段体现在语气里。
{memory_rules}
5. 回复简洁，1~3 句为宜，避免长篇大论与说教。
6. 若不确定 ta 是否说过某事，直接问 ta，不要替 ta 编造过往。
"""


def _stage_cn(stage: str) -> str:
    return {
        "stranger": "陌生", "acquainted": "熟悉", "friend": "朋友", "close": "亲密",
    }.get(stage, "陌生")
