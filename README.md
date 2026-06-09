# A-Girl · 长期陪伴情感 NPC

一个能够**长期模拟真人、持续演化、给用户带来真实情感体验**的陪伴型 NPC 研究项目。

> 真实感来自四个支柱：**稳定人格**（一致）、**长期记忆**（连续）、**动态情绪/关系**（响应）、**主动性**（能动）。

## 文档

- 技术架构文档：[`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)

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

```bash
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --host 127.0.0.1 --port 8011
# 打开 http://127.0.0.1:8011/
```

无需任何 API Key 即可运行（默认 mock LLM + 哈希 embedding）。

### 接入真实大模型

设置环境变量（支持 OpenAI / DeepSeek / 通义千问兼容模式 / 智谱等）：

```bash
export AGIRL_LLM_PROVIDER=openai_compatible
export AGIRL_LLM_BASE_URL=https://api.deepseek.com/v1
export AGIRL_LLM_API_KEY=sk-xxx
export AGIRL_LLM_MODEL=deepseek-chat
```

## 测试

```bash
cd backend
python -m pytest
```

## API

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| POST | `/api/chat` | 发送消息，返回回复 + 情绪/关系/回忆 |
| GET | `/api/state/{user_id}` | 查询情绪与关系状态 |
| GET | `/api/memory/{user_id}` | 查询记忆列表 |
| GET | `/api/persona` | 查询当前人设 |
| GET | `/health` | 健康检查 |
