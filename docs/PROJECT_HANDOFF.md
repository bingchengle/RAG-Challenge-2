# 泰迪杯 B 题「智能问数」— 工程交接报告

> **用途**：克隆仓库到新机器后，把本文件交给 Cursor 或人工阅读，即可对齐架构、已完成项与后续工作。  
> **仓库**：`RAG-Challenge-2`，主代码包 **`finance_agent_rag/`**（原根目录 `src/` 已删除，逻辑已迁入包内）。

---

## 1. 赛题任务与工程对应

| 赛题方向 | 代码入口 / 说明 |
|----------|----------------|
| **任务一** | 财报 PDF → Docling 解析 → **规则从表格抽四表字段**（无 LLM）→ 校验 → **MySQL** 入库 |
| **任务二** | 自然语言问数（附件4）、SQL、多轮、澄清、出图 → `task2.json`、`result_2.xlsx` |
| **任务三** | 库内查数 + 研报 RAG、多意图、归因、表格 references → `result_3.xlsx` 等 |

根入口：`main.py` → `finance_agent_rag.main`（当前为打印路径与占位说明）。  
流水线汇总：`finance_agent_rag/pipeline/run_all.py`（尚未用 argparse 挂子命令，仅提示见各 task）。

---

## 2. 整体框架（目录与职责）

```
finance_agent_rag/
├── config.py                 # BUNDLE 路径、示例/全量切换、附件路径、输出路径
├── core/
│   ├── database/             # schema.sql、db、loader、data_check、schema_fields
│   ├── extraction/           # 附件1 索引、文件名身份、长文本、规则抽数 `rule_task1`、身份合并 `task1_payload`
│   └── pdf_parser/           # Docling PDFParser、表序列化、合并工具
├── llm/                      # 智谱 GLM + BGE 环境、api_requests、prompts、并行处理
├── rag/                      # 向量/BM25、检索、重排、generator（QuestionsProcessor）
├── agents/                   # 多智能体（澄清、SQL、RAG 等）— 与任务二/三衔接
├── memory/                   # 槽位与多轮
├── pipeline/
│   ├── task1_pipeline.py     # 任务一主流程（已实现，见下）
│   ├── task2_pipeline.py     # 占位
│   └── task3_pipeline.py     # 占位
└── data/                     # 赛题附件包解压位置（见 §6）
    └── intermediate/parsed_reports/  # Docling 缓存 JSON（git 中 data/ 大文件被忽略）
```

**设计原则**：

- **对话与向量**：**智谱 GLM** + **BGE**（如硅基流动）；`openai` 包仅作 **HTTP 兼容客户端**，不调用 OpenAI 官方 API。配置见根目录 **`.env.example`**。
- **库**：**MySQL**，库名 **`teddy_b`**，表结构见 `core/database/schema.sql`；连接串 **`TEDDY_MYSQL_DSN`**（`pymysql`）。
- **数据根路径**：`config.BUNDLE_ROOT` =  
  `finance_agent_rag/data/{ B题-示例数据|全部数据 }/{ 示例数据|正式数据 }`  
  由环境变量 **`TEDDY_USE_SAMPLE=1`** 切换「示例/全量」。

---

## 3. 任务一数据流（已实现）

1. 遍历 `reports-上交所`、`reports-深交所` 下 PDF；按文件夹区分 **`exchange`**（SH / SZ）。  
2. **`parse_pdf_identity`**：从文件名取 6 位代码 / 深交简称、辅助报告期等。  
3. **`build_lookup` + `resolve_stock`**：用 **附件1** Excel 将代码/简称解析为 `(stock_code, stock_abbr)`。  
4. **`PDFParser`**（Docling）：输出 JSON 到 **`PARSED_REPORTS_DIR`/`{pdf_stem}.json`**，有缓存则跳过。  
5. **`flatten_report_to_text`**：正文块 + 表格区 **Markdown**（`only_parse` 时用于测长度；抽数以表格 **Markdown 解析** 为主）。  
6. **`rule_task1.extract_financial_payload_from_report`**：从解析 JSON 的 `tables` 行匹配中文字段 + **`task1_payload.apply_identity_to_tables`** 补全主键/报告期（报告期：正文正则 + 深交所 hint + 上交披露日**粗回退**）。  
7. **`data_check.check_payload_for_upsert`**：主键、**报告期**（如 `2023Q1`、`2022HY`、`2021FY`）、四表一致等。  
8. **`loader.upsert_all_tables`**：`INSERT ... ON DUPLICATE KEY UPDATE` 写四表。

**四张表**（主键均为 `(stock_code, report_period)`）：

- `core_performance_indicators_sheet`
- `balance_sheet`
- `cash_flow_sheet`
- `income_sheet`

**任务一 CLI 式运行**（在仓库根）：

```bash
# 小样本
set TEDDY_USE_SAMPLE=1

# 仅解析（不抽数 / 不写库）— 用于验证 Docling
python -m finance_agent_rag.pipeline.task1_pipeline -n 1 --only-parse

# 抽数+校验，但不写入 MySQL（不调用大模型；若报告期仍推断失败会校验报错）
python -m finance_agent_rag.pipeline.task1_pipeline -n 1 --skip-db

# 全链路（需 TEDDY_MYSQL_DSN；任务一**不依赖** GLM/BGE API）
python -m finance_agent_rag.pipeline.task1_pipeline -n 1
```

环境变量等效：  
`TEDDY_TASK1_ONLY_PARSE=1`、`TEDDY_TASK1_SKIP_DB=1`。

---

## 4. 已完成的开发内容（截至交接时）

- **仓库结构**：`finance_agent_rag` 包、根 `main.py` / `setup.py` / `requirements.txt` / `.env.example`、`.gitignore`（**大体积 `data/*` 与 `output` 不提交**）。  
- **任务一**：
  - `core/extraction/`：公司索引、报告身份、**`rule_task1`** 表格规则抽数、**`task1_payload`** 与身份合并；`llm_task1` 仅作兼容 re-export。  
  - `core/database/`：`schema.sql`、`schema_fields.py`、**loader**、**data_check**（入库前强校验；`run_all_checks` 仍为全库级占位）。  
  - **`pipeline/task1_pipeline.py`**：上述全流程 + **`only_parse` / `skip_upsert`** 小测开关。  
- **RAG/LLM 基座**：`llm/`、`rag/`、`core/pdf_parser/` 自原 RAG Challenge 迁移；`QuestionsProcessor` 等仍在包内。  
- **代码已推送**：远程 **`origin/main`**（以 `git log` 为准，例如含 `remove legacy src` 与 `add finance_agent_rag package` 的提交）。

**尚未在仓库中跟踪的内容**（需各机器自备）：

- 赛题 **附件包**（请解压到 `finance_agent_rag/data/` 下，与 `config` 中目录名一致）。  
- 根目录 **`.env`**（从 `.env.example` 复制并填写密钥/DSN）。

---

## 5. 后续工作建议（按优先级）

### 5.1 新机器任务一联调

1. Python 3.10+、创建 venv，`pip install -r requirements.txt`，`pip install -e .`。  
2. 安装/配置 **MySQL**，执行 `finance_agent_rag/core/database/schema.sql`。  
3. 配置 **`.env`** 至少含 **`TEDDY_MYSQL_DSN`**；任务一抽数不调用 GLM，但任务二/三若在本机跑，仍要配 `GLM`/`BGE`（见 `.env.example`）。  
4. 放置赛题数据；**示例**：`set TEDDY_USE_SAMPLE=1`。  
5. **Docling 依赖 PyTorch / EasyOCR**：有 GPU 可装带 CUDA 的 `torch`；无 GPU 用 CPU 版。若 Windows 出现 **`c10.dll` / Error 1114**，安装 **VC++ 2015–2022 x64 运行库** 或从 [pytorch.org](https://pytorch.org) 装 **CPU 官方轮**。  
6. 先 **`-n 1 --only-parse`**，再 **`--skip-db`**，最后全链路。

### 5.2 任务一可深化项

- 在 **`rule_task1.py`** 中扩充**行名关键词**、改进表类型打分，提高抽全率。  
- 上交/深交**个别文件名**未匹配时，补充规则或回退策略。  
- **`infer_report_period`**：正文抽不到时依赖披露日**粗回退**，可按赛题再细化。  
- `data_check.run_all_checks()`：**跨表/跨行**一致性（若赛题有自动评分细则）。  
- 解析/抽数**失败重试、日志与统计**、批量**并行**（注意 DB 并发）。  
- `finance_agent_rag/README.md` 中部分「待实现」表述可能已过时；以本 handoff 为准。

### 5.3 任务二、任务三

- `pipeline/task2_pipeline.py`、`task3_pipeline.py` 仍为 **`NotImplementedError`**。  
- 需组合 **`agents/`**、**`memory/`**、**`rag/generator`（`QuestionsProcessor`）** 与 `config` 中附件4/6 及输出路径。  
- `pipeline/run_all.py`：可扩展为子命令行入口。

---

## 6. 数据与忽略规则（新机器必看）

- Git **不包含** `finance_agent_rag/data/*` 下的大文件（`gitkeep` 仅保留空 `data` 目录占位），也忽略 **`finance_agent_rag/output/`**。  
- 新机器需**自行解压**赛题「附件1～6」到 **`finance_agent_rag/data/<B题-示例数据|全部数据>/<示例数据|正式数据>/`**，目录名需与 `config` 中中文路径一致。  
- **解析缓存**：`finance_agent_rag/data/intermediate/parsed_reports/*.json`（可删缓存强制重解析）。

---

## 7. 给 Cursor 的「续上进度」短指令（可复制）

在仓库根打开文件夹，新建聊天，可粘贴：

> 已读 `docs/PROJECT_HANDOFF.md`。当前任务一主线在 `pipeline/task1_pipeline.py`；库表在 `core/database/`。我新机环境已装好依赖与 MySQL。请先帮我做：【在此写你的具体一步，例如「跑 1 个 PDF 的 only-parse 并排查错误」或「开始实现 task2_pipeline」】。请优先引用 `@docs/PROJECT_HANDOFF.md` 与相关 `@finance_agent_rag/...` 文件。

---

## 8. 关键文件速查

| 项目 | 路径 |
|------|------|
| 全局配置 | `finance_agent_rag/config.py` |
| 任务一 | `finance_agent_rag/pipeline/task1_pipeline.py` |
| 规则抽数 | `finance_agent_rag/core/extraction/rule_task1.py` |
| 身份合并 | `finance_agent_rag/core/extraction/task1_payload.py` |
| 长文本 | `finance_agent_rag/core/extraction/text_flatten.py` |
| 建表 SQL | `finance_agent_rag/core/database/schema.sql` |
| 入库 | `finance_agent_rag/core/database/loader.py` |
| 校验 | `finance_agent_rag/core/database/data_check.py` |
| 环境样例 | `.env.example` |
| 新机连 MySQL（本机/远程/防火墙） | [`docs/MYSQL_CONNECT.md`](MYSQL_CONNECT.md) |

---

*文档与当前代码状态一致；若你后续有提交，可在本节追加「更新日期 + 简短变更说明」。*
