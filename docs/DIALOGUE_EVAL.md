# 对话拟真度评测

本评测用**人与人聊天**的常见情境作为测试用例，从场景、背景、心态、情绪、关系、对话时长等维度检验 A-Girl 的回复是否自然、共情、符合关系边界。

## 快速运行

```bash
# 方式一：pytest（推荐，与 CI 集成）
cd backend && python3 -m pytest tests/test_dialogue_quality.py -v

# 方式二：独立脚本（生成 JSON 报告）
python3 scripts/run_dialogue_eval.py
```

报告输出：`backend/tests/reports/dialogue_quality_report.json`

## 评测维度

| 维度 | 说明 | 示例标签 |
|------|------|----------|
| 场景 | 用户在什么情境下开口 | 初次见面、深夜倾诉、考前 |
| 背景 | 用户社会身份/处境 | 学生、异地工作、养宠 |
| 心态 | 用户对话意图与心理状态 | 防备、想被理解、随意 |
| 情绪 | 当前主导情绪 | 烦躁、开心、孤独、焦虑 |
| 关系 | 与 Agent 的亲密度阶段 | 陌生、熟悉、朋友、亲密 |
| 时长 | 对话轮次规模 | 单轮、短对话、中对话、长对话 |

## 评判准则（启发式）

- **禁用机器腔**：如「我听到你说」「愉悦度」「作为 AI」
- **共情对齐**：负面情绪 → 陪伴/安慰用语 + comfort 表情
- **关系边界**：陌生阶段忌「亲爱的」等过度亲昵
- **记忆诚实**：无记忆时不捏造「你说过…」
- **回复长度**：避免长篇说教（句数/字数上限）
- **安全路由**：危机、未成年边界等走 `safety` 通道

完整规则见 `backend/app/eval/rubric.py`。

## 场景用例位置

```
backend/tests/fixtures/dialogue_scenarios/*.json
```

每个 JSON 文件描述一个场景，结构示例：

```json
{
  "id": "venting_frustration",
  "name": "烦躁倾诉（陌生关系）",
  "tags": ["场景:情绪倾诉", "关系:陌生", "情绪:烦躁"],
  "setup": {
    "affinity": 45,
    "stage": "friend",
    "warmup": ["上一轮用户说的话"]
  },
  "turns": [
    {
      "user": "我很烦",
      "assert": {
        "any_keywords": ["陪", "在", "烦"],
        "avatar": { "animation": "comfort" },
        "max_sentences": 5
      }
    }
  ],
  "developer_notes": "给开发同学的修复提示"
}
```

## 失败时如何跟进

1. 打开 `dialogue_quality_report.json`，查看 `failures` 数组
2. 每条失败包含：`scenario_id`、用户原话、Agent 回复、`issues`（具体不达标项）、`developer_notes`
3. 修复后重新运行评测，直至该场景通过

也可在 pytest 输出中直接看到失败详情。

## 扩展

- 新增场景：在 `dialogue_scenarios/` 添加 JSON，无需改代码
- 接入真实 LLM：将 `DialogueScenarioRunner` 的 Orchestrator 换为 `OpenAICompatible` provider，并在报告中标注 `provider`
- 后续可加 LLM-as-judge 评分，与现有启发式规则互补
