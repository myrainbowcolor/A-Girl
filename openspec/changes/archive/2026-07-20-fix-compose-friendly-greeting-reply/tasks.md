## 1. 实现

- [x] 1.1 `dialogue_compose.py`：导入 `is_friendly_greeting_utterance`，扩展友好问候分支覆盖「你好呀」「嗨，第一次来」
- [x] 1.2 确保陌生关系初识问候语气克制、至多一个问句、不以「嗯」开头

## 2. 测试

- [x] 2.1 `test_dialogue_compose.py`：新增 `test_compose_friendly_greeting_nihao_ya` 与 `test_compose_friendly_greeting_first_visit`
- [x] 2.2 全量 pytest + `run_dialogue_quality.py --strict` 通过

## 3. 归档准备

- [x] 3.1 `npx openspec validate --specs` 通过
