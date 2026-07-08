## 1. Compose 关系阶段感知

- [x] 1.1 `dialogue_compose.py` 增加 stage 归一化辅助函数与 `relationship_stage` 参数
- [x] 1.2 想念、倚靠、续聊、加班等分支用 stage + prior_assistant 双通道判断亲密/朋友

## 2. Orchestrator 传参

- [x] 2.1 `orchestrator._generate_chat_reply` 传入 `relationship.stage.value`
- [x] 2.2 `polish_reply` / `_finalize_reply` 传递 `relationship_stage` 避免 filler 回退丢失亲密语境

## 3. 测试与验证

- [x] 3.1 `test_dialogue_compose.py` 增加亲密首轮想念（无历史）与朋友想念 stage 断言
- [x] 3.2 `cd backend && python -m pytest --ignore=tests/test_dialogue_quality.py -q`
- [x] 3.3 `python scripts/run_dialogue_quality.py --strict` 与 `pytest tests/test_dialogue_quality.py -q`
- [x] 3.4 `npx openspec validate --specs`
