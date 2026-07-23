# 外部知识库

## 狗头军师（goutoujunshi）

来源：[powerycy/goutoujunshi](https://github.com/powerycy/goutoujunshi)

- 核心知识：`references/knowledge/`（20 份）
- 实用沟通：`references/practical/`
- 行为规则：`SKILL.md`

克隆到 `knowledge/vendor/goutoujunshi/` 后分块写入 SQLite 记忆流（scope=`__knowledge__`），对话时按相关度检索注入 prompt。

### 入库

```bash
bash scripts/ingest-goutoujunshi-knowledge.sh
```

或启动服务时自动入库（默认开启 `AGIRL_KNOWLEDGE_AUTO_INGEST=true`）。

### API

```bash
curl http://127.0.0.1:8011/api/knowledge/status
curl -X POST "http://127.0.0.1:8011/api/knowledge/ingest/goutoujunshi?reingest=true"
```

### 许可

狗头军师仓库采用 MIT 许可，详见上游 `LICENSE`。
