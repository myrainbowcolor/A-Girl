## Context

`compose_contextual_reply` 在封闭极简附和分支（line ~933）仅覆盖 `("嗯", "哦", "额", "好", "行")`，遗漏「嗯嗯」。同时 mock 的 filler 投诉分支（`"嗯嗯" in text`）与 `reply_guard.user_complains_filler`、`persona._FILLER_COMPLAINT_KEYWORDS` 将整句「嗯嗯」误判为投诉，抢先于 mock 极简附和分支返回道歉话术。

## Goals / Non-Goals

**Goals:**
- 整句「嗯嗯」在 compose 路径返回与「嗯」一致的陪伴边界接话
- mock/persona/reply_guard 不再将纯「嗯嗯」附和误判为 filler 投诉
- 「能别嗯嗯的回答吗」等真实投诉仍正确触发道歉/认真接话
- 补充单测，保持 26 场景 strict 全绿

**Non-Goals:**
- 不改无聊闲聊上文 + 极简附和分支（已有 `has_casual_social_context` 处理）
- 不改主动消息调度、安全策略、记忆召回

## Decisions

1. **集中识别于 `sentiment_lexicon.py`**：新增 `user_complains_filler_reply(text)`，整句极简附和（`嗯`/`嗯嗯`/`嗯嗯嗯` 等）返回 False；含「敷衍」「别嗯」「不要嗯」或「嗯嗯」+ 否定/请求词（别、不要、一直、能别等）返回 True。
2. **compose 最小改动**：在封闭极简分支 tuple 加入「嗯嗯」，复用现有「我在这儿呢。不急着说…」模板。
3. **mock 对齐**：将 filler 投诉检测改为调用 `user_complains_filler_reply`，使「嗯嗯」落入下方极简附和分支。

## Risks / Trade-offs

- **漏检投诉**：去掉裸 `"嗯嗯"` 子串匹配后，仅含「嗯嗯」无否定词的句子不再触发投诉 → 符合预期（附和不应道歉）
- **误判长句**：「嗯嗯我知道了别嗯嗯」类混合句 → 否定词 + 「嗯嗯」仍触发投诉

## Migration Plan

无数据迁移。部署后即生效。

## Open Questions

（无）
