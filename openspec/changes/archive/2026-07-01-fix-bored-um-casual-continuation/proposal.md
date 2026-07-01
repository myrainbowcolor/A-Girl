## Why

对话质量评测 26 场景全绿，无 open `dialogue-quality` Issue。但 `latest.json` transcript 中 `bored_smalltalk` 第 2 轮显示：用户先说「好无聊啊」后仅回「嗯」，NPC 却答「我在这儿呢。不急着说，你想开口了再说~」——这是封闭/低落语境的接话，与无聊摸鱼闲聊语境不符，听感像把用户当情绪低落对待，削弱拟真陪伴感。

## What Changes

- 在 `sentiment_lexicon.py` 增加「近期无聊/社交闲聊语境」检测辅助函数
- `dialogue_compose.py`：极简「嗯/哦/好」在无聊闲聊上文时返回轻松续聊，不走封闭边界套话
- `mock.py`：场景分支与 compose 对齐，同样在上文含无聊标记时差异化极简回复
- 补充单元测试覆盖 `bored_smalltalk` 第 2 轮接话

## Capabilities

### New Capabilities

（无）

### Modified Capabilities

- `persona`：口语化回复约束增加「无聊闲聊上文 + 极简嗯」场景须轻松续聊、禁止封闭边界套话

## Impact

- `backend/app/sentiment_lexicon.py`
- `backend/app/dialogue_compose.py`
- `backend/app/llm/mock.py`
- `backend/tests/test_dialogue_compose.py`
- 不影响安全、危机干预、记忆主路径；`short_reply_user` 等真正封闭场景行为不变
