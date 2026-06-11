# AGENTS.md

## 项目概述

**A-Girl** 是一个情感陪伴 Agent 研究仓库：长期记忆、动态情绪/关系、安全护栏与数字人表现。

主要代码在 `backend/`，文档在 `docs/`。

## 开发环境

| 项目 | 说明 |
|------|------|
| 语言 | Python 3.12+ |
| 框架 | FastAPI |
| 依赖 | `backend/requirements.txt` |
| 配置 | `backend/.env.example` |

```bash
cd backend && pip install -r requirements.txt
```

## 常用命令

```bash
# 启动服务
cd backend && python3 -m uvicorn app.main:app --host 127.0.0.1 --port 8011

# 全量测试
cd backend && python3 -m pytest

# 对话拟真度场景评测（多维度人机对话质量）
cd backend && python3 -m pytest tests/test_dialogue_quality.py -v
python3 scripts/run_dialogue_eval.py   # 输出 backend/tests/reports/dialogue_quality_report.json

# LLM 连通性
cd backend && python3 scripts/check_llm.py
```

## 对话质量评测

- 场景用例：`backend/tests/fixtures/dialogue_scenarios/*.json`
- 评判规则：`backend/app/eval/rubric.py`
- 失败报告：`backend/tests/reports/dialogue_quality_report.json`（gitignore，本地/CI 生成）
- 说明文档：`docs/DIALOGUE_EVAL.md`

## Cursor Cloud specific instructions

- **依赖**：`pip install -r backend/requirements.txt`
- **默认无外部 LLM**：使用 Mock LLM，可直接跑测试与对话评测
- **Git**：在 `/workspace` 根目录操作；默认分支为 `main`
- **分支命名**：Cloud Agent 功能分支请使用 `cursor/<描述>-ff3f` 格式
