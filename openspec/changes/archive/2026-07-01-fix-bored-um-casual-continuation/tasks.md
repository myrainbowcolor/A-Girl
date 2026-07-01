## 1. 语境检测

- [x] 1.1 在 `sentiment_lexicon.py` 新增 `has_casual_social_context(prior_text)`，复用 `CASUAL_SOCIAL_MARKERS` 与负面排除块

## 2. 回复分支

- [x] 2.1 `dialogue_compose.py`：无聊上文 + 极简附和（嗯/哦/好）时返回轻松续聊，插入于通用封闭极简分支之前
- [x] 2.2 `mock.py` `_scene_reply`：与 compose 对齐，同样在上文含无聊标记时差异化极简回复

## 3. 测试与验证

- [x] 3.1 `test_dialogue_compose.py` 增加无聊上文「嗯」与封闭场景「嗯」对照测试
- [x] 3.2 跑 `pytest`（忽略 dialogue_quality）+ `run_dialogue_quality.py --strict` + `test_dialogue_quality.py` 全绿
- [x] 3.3 `npx openspec validate --specs` 通过
