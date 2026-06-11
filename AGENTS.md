# AGENTS.md

## 项目概述

**A-Girl** 是一个情感陪伴 Agent 的研究仓库（见 GitHub 描述）。当前 `main` 分支仅包含占位文件：

- `README.md` — 项目标题
- `LICENSE` — MIT 许可证

尚无应用代码、依赖清单、测试或 CI 配置。

## 开发环境

| 项目 | 状态 |
|------|------|
| 语言 / 框架 | 未定义 |
| 包管理器 | 无（无 `package.json`、`requirements.txt` 等） |
| 环境变量 | 无 `.env` 或文档 |
| Docker / Compose | 无 |

克隆仓库后即可工作，无需安装依赖。

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

- **无依赖安装步骤**：VM 启动时的 `update_script` 为无操作（`true`），因为仓库没有 lockfile 或依赖清单。
- **无可启动服务**：没有前端、后端、数据库或 Docker Compose 配置；无法执行端到端应用演示，直到实现代码并入仓库。
- **Git**：在 `/workspace` 根目录操作；默认分支为 `main`。
- **分支命名**：Cloud Agent 功能分支请使用 `cursor/<描述>-ff3f` 格式。
- **添加代码后**：请同步更新 `README.md`（安装与运行说明）、依赖文件，以及本文件中的命令与服务说明。
