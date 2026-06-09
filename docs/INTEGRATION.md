# 游戏嵌入集成指南

A-Girl 同一套后端支持两种部署模式，独立 Web 与游戏共用同一 HTTP API：

- **standalone（独立）**：后端自带 Web 聊天 UI（含数字人 + 语音）。
- **embedded（嵌入游戏）**：游戏客户端（Lua / Unity 等）通过 HTTP 调用后端，自行渲染游戏内数字人；用响应里的 `avatar` 驱动表情/动作，用 `tts` 音频做配音。

> 研究阶段为单玩家（1:1）。`user_id` 用稳定的玩家标识即可（如存档 ID）。

## 1. 启动后端（嵌入模式）

```bash
cd backend
pip install -r requirements.txt
# 嵌入模式：仅提供 API；面向未成年人；接 OpenAI 或自托管
export AGIRL_DEPLOYMENT_MODE=embedded
export AGIRL_AUDIENCE=minor
# 真实模型（可选，缺省走离线 mock）
export AGIRL_LLM_PROVIDER=openai_compatible
export AGIRL_LLM_BASE_URL=https://api.openai.com/v1   # 自托管改为你的地址
export AGIRL_LLM_API_KEY=sk-xxx
export AGIRL_LLM_MODEL=gpt-4o-mini
python -m uvicorn app.main:app --host 0.0.0.0 --port 8011
```

## 2. 核心接口契约

### POST `/api/chat`

请求：

```json
{ "user_id": "player-001", "message": "你好呀", "session_id": "save-001" }
```

响应（游戏据此驱动数字人）：

```jsonc
{
  "reply": "嘿，今天过得怎么样呀？",
  "emotion": { "pleasure": 0.6, "arousal": 0.3, "dominance": 0.0, "label": "开心又有点小兴奋" },
  "relationship": { "affinity": 12.0, "stage": "acquainted" },
  "avatar": { "expression": "微笑", "intensity": 0.7, "animation": "nod" },
  "retrieved_memories": ["ta 说：我养了一只叫橘子的猫"],
  "is_crisis": false,
  "safety_category": null,
  "llm": "openai_compatible:gpt-4o-mini",
  "tts": null
}
```

字段说明：

| 字段 | 游戏用途 |
| --- | --- |
| `reply` | 显示/朗读的文本 |
| `emotion.label` | 可用于气泡/UI 情绪提示 |
| `avatar.expression` | 数字人表情：微笑/大笑/难过/担心/惊讶/平静 |
| `avatar.intensity` | 表情强度 0~1，控制夸张程度 |
| `avatar.animation` | 建议肢体动作：idle/wave/nod/comfort/cheer |
| `relationship.stage` | 关系阶段，可解锁剧情/称呼 |
| `is_crisis`/`safety_category` | 触发安全分支时游戏可切换更克制的表现 |

### POST `/api/tts`（按需取语音）

```json
{ "text": "嘿，今天过得怎么样呀？" }
```

返回 `audio_base64`（wav）+ `duration_ms`（供口型/动画对齐）。

> 嵌入模式默认不在 `/api/chat` 内联音频（省带宽）。需要时单独调 `/api/tts`，或设 `AGIRL_CHAT_INCLUDE_TTS=true` 让 chat 直接带音频。

### POST `/api/stt`（玩家语音输入）

```json
{ "audio_base64": "...", "format": "wav" }
```

返回识别文本，再投喂给 `/api/chat`。

## 3. 表情/动作 → 游戏资源映射建议

游戏侧维护一张映射表，把后端语义化线索对应到自家 Live2D/3D 资源：

| expression | Live2D 表情 | animation | 骨骼动画 |
| --- | --- | --- | --- |
| 微笑 | exp_smile | nod | anim_nod |
| 大笑 | exp_laugh | cheer | anim_cheer |
| 难过 | exp_sad | idle | anim_idle |
| 担心 | exp_worried | comfort | anim_comfort |
| 惊讶 | exp_surprised | idle | anim_idle |
| 平静 | exp_neutral | idle | anim_idle |

口型：用 `tts.duration_ms` 做简单开合循环，或后续接入 viseme 时序。

## 4. Lua 客户端示例

见 [`examples/lua_client.lua`](../examples/lua_client.lua)，演示从 Lua 发起 `/api/chat` 请求并解析 `reply` 与 `avatar`，可直接对接到游戏内伙伴系统（如 `PartnerDojoCtrl`）。
