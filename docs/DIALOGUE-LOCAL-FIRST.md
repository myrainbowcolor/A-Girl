# 本地场景优先对话方案（游戏 NPC 拟真）

> 目标：**尽量不用云 LLM**，对话自然、前后有逻辑，且**不跑出游戏世界观**。

## 1. 为什么不用云 LLM 做主生成

| 云 LLM 问题 | 游戏 NPC 需求 |
|-------------|---------------|
| 易输出客服腔、英文、「作为 AI…」 | 固定人设小语，中文口语 |
| 易给现实世界的无关建议（写公文、查资料） | 只在游戏/当前关系语境里陪伴 |
| 延迟与成本不可控 | 嵌入游戏需稳定、可离线 |

结论：**嘴巴可以接本地小模型，但「说什么」应由场景 + 状态决定，而不是让模型自由发挥。**

### Mock 与场景引擎的区别

| 组件 | 用途 | 生产环境 |
|------|------|----------|
| **`SceneReplyEngine`** | 关键词场景分支（加班、宠物、情绪…） | ✅ scene_first 主路径 |
| **`MockLLMProvider`** | pytest/CI 离线测试 | ❌ 勿设 `AGIRL_LLM_PROVIDER=mock` |

场景逻辑在 `app/scene_engine.py`，与 mock 测试 Provider **同源但不同名**；生产不依赖 mock。

## 2. 推荐架构：Scene-First（场景优先）

```
用户输入
   │
   ▼
┌─────────────────┐
│ 1. 场景引擎      │  加班/宠物/情绪/恋爱/边界…（有逻辑的分支）
│   (SceneEngine)  │
└────────┬────────┘
         │ 未命中
         ▼
┌─────────────────┐
│ 2. 上下文拼装    │  随便聊聊/空落落/还行吧/怎么办(承接上文)
│   (Compose)      │
└────────┬────────┘
         │ 仍未覆盖
         ▼
┌─────────────────┐
│ 3. 本地 LLM      │  仅润色/补句；system 含【游戏世界观】硬约束
│   (llama-cpp)    │  temperature≤0.6，max_tokens≤120
└────────┬────────┘
         │ 输出越界/嗯嗯/空套话
         ▼
┌─────────────────┐
│ 4. 兜底          │  短句陪伴 / 场景 fallback（禁止问卷式「后来呢」）
│   (Guard)        │
└─────────────────┘
```

与旧 **Local Blend** 的区别：

| 策略 | 行为 | 适用 |
|------|------|------|
| `scene_first` | 先场景→拼装→本地 LLM；LLM 只做最后手段 | **游戏嵌入（默认推荐）** |
| `local_blend` | 场景与 LLM 并行，坏回复再回退 | 独立 Web 调试 |
| `local_llm` | 主要靠本地模型 | 不推荐（0.5B~1.5B 仍易僵） |

## 3. 配置（无需云 Key）

```bash
# backend/.env 或 scripts/start-local-game.sh 自动生成
AGIRL_DIALOGUE_STRATEGY=scene_first
AGIRL_LLM_PROVIDER=openai_compatible
AGIRL_LLM_BASE_URL=http://127.0.0.1:11435/v1   # 本机 llama-cpp
AGIRL_LLM_MODEL=qwen2.5-1.5b-instruct          # 比 0.5B 自然，仍纯本地
AGIRL_SCENE_FALLBACK=true

# pytest/CI 才用 mock；生产路径是 SceneReplyEngine，不是 MockLLMProvider

# 游戏世界观（注入 system，禁止聊界外内容）
AGIRL_GAME_WORLD_BRIEF=你是「星港城」里的陪伴者小语。只聊城里的事、冒险见闻和玩家心情。不要提现实公司、公文写作、联网查资料。
```

启动：

```bash
bash scripts/start-local-game.sh
```

## 4. 三层「自然度」来源

1. **状态驱动**（已有）：人格、情绪、关系、记忆检索 → prompt 与场景参数  
2. **场景库**（持续扩充）：关键词 + 上下文（上文是否提到猫/老板）→ 有逻辑的句子  
3. **本地 LLM**（可选润色）：只改写措辞，不改变事实；越界由 `in_world_guard` 丢弃  

**不要指望 0.5B/1.5B 独自撑起开放闲聊**；自然度来自 1+2，3 是补充。

## 5. 世界观与越界防护

`in_world_guard` 拦截：

- 中文对话里整段英文客服回复  
- 「How can I assist」「作为语言模型」  
- 明显公文/教程体（「以下是」「首先其次」）  

`persona` 在设置 `GAME_WORLD_BRIEF` 后追加：

- 不得引入世界观外实体与建议  
- 不会帮写现实文书；可改为「我陪你理理为什么想这么做」  

## 6. 本地模型选型（无云）

| 模型 | 体积 | 建议 |
|------|------|------|
| Qwen2.5-0.5B Q4 | ~400MB | 不推荐（易嗯嗯/空套话） |
| Qwen2.5-1.5B Q4 | ~1GB | 低配机器 |
| **Qwen2.5-3B Q4** | **~2GB** | **默认推荐** |
| Qwen2.5-7B Q4 | ~4.7GB | 16GB+ 内存可试 `AGIRL_LOCAL_LLM_TIER=7b` |

均通过 `llama-cpp-python` + HuggingFace GGUF，与现有 `examples/llama_cpp_server.py` 兼容。

## 7. 游戏侧接入要点

1. `user_id` / `session_id` 用存档 ID，保证记忆连续  
2. `AGIRL_DEPLOYMENT_MODE=embedded`  
3. 把当前任务/地点/队伍摘要写入 `AGIRL_GAME_WORLD_BRIEF`（或后续专用 API 字段）  
4. 不要用云 API Key；TTS 可用 Edge（与对话内容无关）  

## 8. 后续迭代（OpenSpec 可拆 Issue）

- [ ] 场景库 YAML/JSON 热更新（策划可配）  
- [ ] `compose` 接 `recent_messages` 做指代（「它」「怎么办」）  
- [ ] 本地 3B + 仅 paraphrase 模式（scene 产出 draft → LLM 改写）  
- [ ] 按 `dialogue_quality` 场景库持续回归  

## 9. 验收标准

- 开放闲聊（随便聊聊、空落落）不再出现「愿意多说一点吗」「有什么新鲜事」  
- 中文用户不出现英文客服腔  
- 「帮我写辞职信」类请求不跑题到「当众被骂」  
- 同一 session 多轮「猫 → 打翻 → 怎么办」逻辑连贯  
- 全程无云 LLM 调用  
