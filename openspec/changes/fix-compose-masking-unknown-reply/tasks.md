## 1. 实现

- [x] 1.1 在 `dialogue_compose.py` masking 分支扩展 `text in (...)` 加入「不知道」「说不上」；模板去句首「嗯」，与 mock 语义对齐
- [x] 1.2 在 `test_dialogue_compose.py` 新增 `test_compose_masking_unknown_reply` 与 `test_compose_masking_shuobushang_reply` 探针

## 2. 验证

- [ ] 2.1 `cd backend && python3 -m pytest --ignore=tests/test_dialogue_quality.py -q`
- [ ] 2.2 `python3 scripts/run_dialogue_quality.py --strict`
- [ ] 2.3 `python3 -m pytest tests/test_dialogue_quality.py -q`
- [ ] 2.4 `cd .. && npx openspec validate --specs`
