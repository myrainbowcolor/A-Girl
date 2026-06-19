# A-Girl · 长期陪伴情感 NPC

一个能够**长期模拟真人、持续演化、给用户带来真实情感体验**的陪伴型 NPC 研究项目。

> 真实感来自四个支柱：**稳定人格**（一致）、**长期记忆**（连续）、**动态情绪/关系**（响应）、**主动性**（能动）。

## 文档

- 技术架构文档：[`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)
- **OpenSpec 规范驱动开发**：[`docs/OPENSPEC.md`](docs/OPENSPEC.md)
- **Automations 自动合并 PR**：[`docs/AUTOMATIONS.md`](docs/AUTOMATIONS.md)

## 核心骨架（已实现）

| 子系统 | 位置 | 说明 |
| --- | --- | --- |
| 人格系统 | `backend/app/persona.py` | 大五人格 + 风格，构建 system 提示 |
| 记忆系统 | `backend/app/memory/` | 记忆流 + 检索打分（相关性/时近性/重要性）+ 反思 |
| 情感系统 | `backend/app/emotion/` | PAD 情绪 + 关系亲密度演化 |
| 安全护栏 | `backend/app/safety.py` | 危机检测与安全话术 |
| 对话编排 | `backend/app/orchestrator.py` | 串联感知→安全→检索→情绪→生成→状态更新 |
| LLM 抽象 | `backend/app/llm/` | OpenAI 兼容 + 离线 mock |
| API/前端 | `backend/app/main.py`, `backend/static/` | FastAPI + 轻量聊天页 |

## 快速开始

> **默认启动 = 真实 LLM；mock 仅用于 pytest / CI。**  
> 直接 `uvicorn` 且无 `.env` 时会静默退化为 mock（模板回复，听不懂你在说什么）。  
> **聊天请用下面推荐方式启动。**

### 推荐：一键启动（LLM + 聊天服务）

```bash
bash scripts/start-remote-llm.sh
# 打开 http://127.0.0.1:8011/
```

脚本会：下载/加载本地 GGUF 或 Ollama 模型 → 起 llama-cpp 服务 → 写 `backend/.env` → 起 A-Girl。

### 或：本机 Ollama / 云端 API

```bash
cp backend/.env.example backend/.env   # 按注释改 LLM 地址与 Key
cd backend && pip install -r requirements.txt
python -m uvicorn app.main:app --host 127.0.0.1 --port 8011
```

```bash
# 本机 Ollama 示例
AGIRL_LLM_PROVIDER=openai_compatible
AGIRL_LLM_BASE_URL=http://127.0.0.1:11434/v1
AGIRL_LLM_API_KEY=ollama
AGIRL_LLM_MODEL=llama3

# 云端 OpenAI / DeepSeek 示例
AGIRL_LLM_BASE_URL=https://api.deepseek.com/v1
AGIRL_LLM_API_KEY=sk-xxx
AGIRL_LLM_MODEL=deepseek-chat
```

### mock 是什么？什么时候用？

| 场景 | LLM |
|------|-----|
| **你实际聊天** | 真实 LLM（Ollama / llama-cpp / API） |
| **pytest / GitHub CI** | mock（确定性、无 Key、快） |
| **对话质量基线** | mock strict（测编排规则，不测模型智商） |

无 Key 时本地验证 OpenAI 兼容链路可用桩服务：`python -m uvicorn examples.openai_stub_server:app --port 9000`，再把 `AGIRL_LLM_BASE_URL` 指向 `http://127.0.0.1:9000/v1`（仍是假回复，不是 mock 模板）。

### 语音（Edge TTS 免费，无需 Key）

### 主动关心

NPC 会在事件到点（生日/面试/考试）、上次情绪低落、长时间未互动时主动发起。客户端轮询：

```bash
curl http://127.0.0.1:8011/api/proactive/<user_id>
```

后台调度器（可选）：`export AGIRL_PROACTIVE_SCHEDULER_ENABLED=true`，再轮询 `/api/proactive/outbox/<user_id>`。

### 数字人与口型同步

`/api/chat` 响应含 `avatar`（表情/动作 + Live2D 参数）；`/api/tts` 返回 `lipsync` 口型轨迹。独立前端用 SVG 数字人演示口型同步，嵌入游戏用 Live2D 参数 + lipsync 驱动。

## 测试

```bash
cd backend
python -m pytest          # conftest 固定 mock LLM，无需外部 API
# 对话拟真度场景评测（多场景/情绪/关系/时长）+ 失败记录
python scripts/run_dialogue_quality.py
# 数字人口型同步的无头浏览器确定性验证（需先启动服务）
pip install -r requirements-dev.txt && python -m playwright install chromium
python scripts/verify_lipsync.py
```

对话质量评测说明见 [`docs/DIALOGUE_QUALITY.md`](docs/DIALOGUE_QUALITY.md)。

## API

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| POST | `/api/chat` | 发送消息，返回回复 + 情绪/关系/回忆 + 数字人表情（需先通过年龄确认） |
| POST | `/api/tts` | 文本转语音（含口型轨迹 lipsync + viseme 序列 + 情绪化风格） |
| POST | `/api/stt` | 语音转文本 |
| POST | `/api/consent` | 年龄确认门（未确认前 `/api/chat` 返回 403） |
| GET | `/api/consent/{user_id}` | 查询是否已确认年龄 |
| GET | `/api/audit/{user_id}` | 家长可见安全审计日志 |
| GET | `/api/stream/{user_id}` | SSE 主动推送实时流 |
| GET | `/api/proactive/{user_id}` | 主动关心检查/投递 |
| GET | `/api/state/{user_id}` | 查询情绪与关系状态 |
| GET | `/api/memory/{user_id}` | 查询记忆列表 |
| GET | `/api/persona` | 查询当前人设 |
| GET | `/health` | 健康检查 |

### 未成年人合规与主动推送

- 年龄确认门默认开启（`AGIRL_REQUIRE_AGE_GATE=true`），可设最小年龄 `AGIRL_MIN_AGE`。
- 安全事件（危机/成人/暴力/隐私）写入家长可见审计日志（`AGIRL_AUDIT_LOG_PATH`）。
- 主动关心可通过 SSE（前端 `EventSource`）或 webhook（`AGIRL_PUSH_WEBHOOK_URL`）推送。
