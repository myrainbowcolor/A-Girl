# 对话拟真度质量评测

本目录说明如何用**场景化测试用例**评估 A-Girl 对话是否「像真人」，并在质量不达标时**记录失败案例**供开发人员修复。

## 评测维度

每个场景标注以下人类对话维度，便于按类型排查：

| 维度 | 示例 |
| --- | --- |
| **场景 (scene)** | 深夜独处、考前自习、节日一个人 |
| **背景 (background)** | 学生、上班族、家长、异地务工 |
| **心态 (mindset)** | 防御、怀旧、冲动、想被理解 |
| **情绪 (emotion)** | 焦虑、开心、愤怒、危机 |
| **关系 (relationship)** | 陌生 / 熟悉 / 朋友 / 亲密 |
| **时长 (duration)** | 单轮、2~3 轮、6 轮长对话 |

用例定义见 `backend/app/dialogue_quality/scenarios.py`。

## 质量规则（启发式）

`DialogueEvaluator` 自动检查包括但不限于：

- **critical**：空回复、机械/客服腔、PAD 数值泄露、危机未给热线、应拦截未拦截
- **major**：负面情绪缺共情、陌生关系过度亲昵、表情与情绪不符、记忆未召回、**连续重复回复**、**机械复述用户原话**、**忽略用户直接提问**、**怀旧/柔和分享时表情过嗨**、**话题未延续**
- **minor**：回复过长、积极情绪偏冷淡、**多轮问卷式追问**

规则 ID 会写入报告，便于对应修改 `persona.py`、`mock.py`、编排逻辑或真实 LLM 提示词。

## 运行方式

```bash
cd backend

# 全量场景 + 生成报告
python scripts/run_dialogue_quality.py

# CI / 严格模式：critical 或 major 问题则 exit 1
python scripts/run_dialogue_quality.py --strict

# 只跑单个场景
python scripts/run_dialogue_quality.py --scenario memory_pet_name

# 按维度筛选（子串匹配）
python scripts/run_dialogue_quality.py --relationship 朋友 --emotion 焦虑
python scripts/run_dialogue_quality.py --duration 6轮 --scene 深夜

# pytest（默认无 critical 即通过，并写入报告）
python -m pytest tests/test_dialogue_quality.py -v
```

## 报告输出

运行后生成（已 gitignore，本地/CI 工件）：

| 文件 | 说明 |
| --- | --- |
| `backend/reports/dialogue_quality/latest.json` | 最近一次完整结果 |
| `backend/reports/dialogue_quality/latest.md` | 开发人员可读的失败摘要 |
| `backend/reports/dialogue_quality/failures.jsonl` | 历史失败流水（追加） |

`failures.jsonl` 每行一条 JSON，包含：

- 场景维度标签
- `issues`（含 `rule_id`、`severity`、`message`、**`fix_hint`**）
- `transcript`（用户/NPC 全文）
- `developer_notes`

`latest.json` 另含 `dimension_index`（按场景/背景/心态/情绪/关系/时长汇总的失败列表）与 `rule_fix_hints` 全局映射。

## 开发人员修复流程

1. 打开 `latest.md` 或 `failures.jsonl`，找到失败场景与 `rule_id`。
2. 阅读 `transcript`，判断是提示词、mock 模板、记忆检索还是安全策略问题。
3. 修改代码后重跑 `run_dialogue_quality.py`。
4. 若新增场景，在 `scenarios.py` 增加 `DialogueScenario` 并补充期望字段。

## 接入真实 LLM

默认使用 `MockLLMProvider` 保证 CI 确定性。对接真实模型时：

```python
from app.config import Settings
from app.llm import OpenAICompatibleProvider  # 按项目实际 provider
from app.dialogue_quality import DialogueQualityRunner, DialogueQualityReporter, all_scenarios

llm = OpenAICompatibleProvider(...)
runner = DialogueQualityRunner(llm=llm, settings=Settings())
results = runner.run_all(all_scenarios())
DialogueQualityReporter().write_run_report(results, llm_name=llm.name)
```

真实 LLM 结果波动大，建议将 `--strict` 仅用于 mock 基线；线上模型用报告人工复核。

## 新增场景模板

```python
DialogueScenario(
    id="unique_id",
    name="可读名称",
    scene="…",
    background="…",
    mindset="…",
    emotion="…",
    relationship="朋友",
    duration="2轮",
    description="期望行为说明",
    turns=[
        TurnSpec("用户第一句话", expect_empathy=True),
        TurnSpec("用户第二句话"),
    ],
    initial_affinity=40.0,
    expectation=ScenarioExpectation(min_affinity_delta=1.0),
)
```
