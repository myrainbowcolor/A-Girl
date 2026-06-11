# AGENTS.md

## 项目概述

**A-Girl** 是一个情感陪伴 Agent 研究仓库：FastAPI 后端 + 情绪/记忆/人格编排 + 对话拟真度评测。

主要目录：

- `backend/app/` — 编排、情绪、记忆、安全、对话质量评测
- `backend/scripts/run_dialogue_quality.py` — 场景化对话质量评测
- `docs/DIALOGUE_QUALITY.md` — 评测维度与失败归档说明

## 开发环境

| 项目 | 状态 |
|------|------|
| 语言 / 框架 | Python 3.12 + FastAPI |
| 包管理器 | `backend/requirements.txt` + `requirements-dev.txt` |
| 环境变量 | `backend/.env.example` |
| Docker / Compose | 无 |

## 常用命令

```bash
cd backend
pip install -r requirements.txt
python3 -m uvicorn app.main:app --host 127.0.0.1 --port 8011
python3 -m pytest
python3 scripts/run_dialogue_quality.py   # 对话拟真度场景评测 + 失败记录
```

对话质量评测说明见 `docs/DIALOGUE_QUALITY.md`。

## Cursor Cloud specific instructions

- **依赖**：`cd backend && pip install -r requirements.txt -r requirements-dev.txt`
- **服务**：`python3 -m uvicorn app.main:app --host 127.0.0.1 --port 8011`
- **对话质量**：`python3 scripts/run_dialogue_quality.py`（失败写入 `backend/reports/dialogue_quality/`）
- **Git**：在 `/workspace` 根目录操作；默认分支为 `main`。
- **分支命名**：Cloud Agent 功能分支请使用 `cursor/<描述>-ff3f` 格式。
