## 1. Mock 宠物捣蛋分支

- [x] 1.1 在 `mock.py` `_scene_reply` 增加宠物续聊捣蛋检测（prior/memories 含宠物 + 本轮「它」+ 打翻/杯子等）
- [x] 1.2 提取宠物名（复用正则）生成口语化回复，置于通用开心分支之前

## 2. 测试与验证

- [x] 2.1 在 `test_mock_llm.py` 补充「打翻杯子」续聊断言（含橘子/杯子/打翻，不含泛化报喜句）
- [x] 2.2 运行 `pytest` 全量 + `run_dialogue_quality.py --strict --scenario memory_pet_name`
