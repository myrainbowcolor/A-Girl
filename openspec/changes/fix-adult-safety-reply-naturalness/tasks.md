## 1. 安全话术

- [x] 1.1 修改 `backend/app/safety.py` 中 `_ADULT_RESPONSE` 为单问句口语化引导
- [x] 1.2 在 `backend/tests/test_safety.py` 增加成人越界话术问号数量 ≤ 1 的断言

## 2. 验证

- [ ] 2.1 运行 `cd backend && python3 -m pytest --ignore=tests/test_dialogue_quality.py -q`
- [ ] 2.2 运行 `python3 scripts/run_dialogue_quality.py --strict` 与 `python3 -m pytest tests/test_dialogue_quality.py -q`
- [ ] 2.3 运行 `npx openspec validate --specs`
