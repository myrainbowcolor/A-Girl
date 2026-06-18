# A-Girl Agent 指南

## OpenSpec（规范驱动开发）

新功能或较大改动请走 OpenSpec，不要直接改代码：

1. **Propose** — 用 Skill `/openspec-propose` 或口述「用 OpenSpec propose：xxx」
2. **Apply** — `/openspec-apply-change` 按 tasks 实现
3. **Archive** — `/openspec-archive-change` 归档

规格真相源：`openspec/specs/`。详细说明见 [docs/OPENSPEC.md](docs/OPENSPEC.md)。

## 在 Cursor 里怎么找到 OpenSpec？

输入 `/` 后看 **Skills**（不是 Commands），搜索 **openspec**，应出现：

- `openspec-propose`
- `openspec-apply-change`
- `openspec-explore`
- `openspec-sync-specs`
- `openspec-archive-change`

若看不到：先 `git pull origin main`，再 **Developer: Reload Window**。

## 项目要点

- 后端：`backend/app/`，测试 `cd backend && python -m pytest`
- 默认受众未成年人，安全优先
- 回复风格：口语化，每轮最多一个问句
