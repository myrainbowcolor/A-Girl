## 1. 实现 compose 失眠反刍分支

- [x] 1.1 在 `dialogue_compose.py` 通用「好烦」短句分支前增加「越躺越清醒」、失眠关键词、项目悬停焦虑分支（对齐 mock.py 话术风格）
- [x] 1.2 在 `test_dialogue_compose.py` 新增 `test_compose_insomnia_rumination_followup`，断言「越躺越清醒，好烦」续聊含反刍共情、不含「突然」「一阵子」问卷句

## 2. 验证

- [x] 2.1 `cd backend && python -m pytest tests/test_dialogue_compose.py -q`
- [x] 2.2 `cd backend && python -m pytest --ignore=tests/test_dialogue_quality.py -q`
- [x] 2.3 `cd backend && python scripts/run_dialogue_quality.py --strict`
- [x] 2.4 `cd .. && npx openspec validate --specs`
