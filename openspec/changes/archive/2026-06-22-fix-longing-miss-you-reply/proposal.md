## Why

对话质量场景 `close_miss_you` 首轮用户说「好久没聊了，有点想你」，当前 mock/scene 路径因 `is_positive_utterance` 含「想你」误命中开心分享分支，回复「哇，听你这么说我也跟着开心起来了！快多跟我说说～」且 avatar 为大笑/cheer——像报喜不像亲密想念，拟真度差。

修复前 transcript 片段：
- 用户：好久没聊了，有点想你
- NPC：亲爱的，（忍不住弯了弯嘴角）哇，听你这么说我也跟着开心起来了！快多跟我说说～
- avatar：大笑 / cheer

## What Changes

- 在 `sentiment_lexicon.py` 增加「想念/依恋」口语识别，区别于纯开心分享；`analyze_lexicon` 对想念句返回温和正向（微笑级，非大笑 cheer）
- 在 `mock.py` 将「想念」分支提前于开心分享分支，并优化亲密/朋友想念话术（柔软黏人、至多一个问句）
- 在 `persona.py` 为用户想念类轮次追加「本轮侧重」语气指引
- 补充单元测试与 `close_miss_you` 场景期望（回复不含「开心起来了」、avatar 非 cheer）
- 不改 orchestrator 主路径、安全策略、API 契约

## Capabilities

### New Capabilities

（无）

### Modified Capabilities

- `persona`: 用户表达想念/好久未见时 prompt 含依恋侧重，禁止套用开心报喜语气
- `emotion-relationship`: 想念类整句情感标注为温和正向（非纯报喜），驱动 avatar 微笑/nod 而非大笑 cheer

## Impact

- `backend/app/sentiment_lexicon.py` — 想念口语识别
- `backend/app/emotion/analyzer.py` — 想念句 sentiment 标注
- `backend/app/llm/mock.py` — 场景分支顺序与想念话术
- `backend/app/persona.py` — 用户轮次语气侧重
- `backend/tests/test_sentiment_lexicon.py`、`backend/tests/test_mock_llm.py`、`backend/tests/test_persona.py` — 回归测试
- `backend/app/dialogue_quality/scenarios.py` — close_miss_you 期望加强（可选）
