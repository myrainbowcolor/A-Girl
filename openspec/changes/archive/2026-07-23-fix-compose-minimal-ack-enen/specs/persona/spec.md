## ADDED Requirements

### Requirement: 整句嗯嗯极简附和 compose 回应

用户整句仅为极简附和「嗯嗯」时，生产路径 `compose_contextual_reply` MUST 返回与「嗯」「哦」「好」一致的 1 句陪伴边界接话（如「我在这儿呢。不急着说，你想开口了再说~」），禁止落入问卷式 open 兜底；回复 MUST NOT 以「嗯」开头。`user_complains_filler_reply` MUST NOT 将整句「嗯嗯」误判为 filler 投诉；含「别嗯嗯」「太敷衍」等否定/投诉语义时仍 MUST 触发 filler 投诉路径。

#### Scenario: 生产路径 compose 整句「嗯嗯」

- **WHEN** `compose_contextual_reply` 处理整句「嗯嗯」且无无聊闲聊上文
- **THEN** 返回陪伴边界接话，不返回 `None` 或问卷式 open 兜底；回复 MUST NOT 以「嗯」开头

#### Scenario: mock 整句「嗯嗯」不误判投诉

- **WHEN** mock 场景分支处理整句「嗯嗯」
- **THEN** 返回极简附和接话，不返回「抱歉刚才太敷衍了」类道歉话术

#### Scenario: filler 投诉「能别嗯嗯」仍触发

- **WHEN** 用户说「能别嗯嗯的回答吗」
- **THEN** `user_complains_filler_reply` 返回 True，NPC 走 filler 投诉/道歉接话路径
