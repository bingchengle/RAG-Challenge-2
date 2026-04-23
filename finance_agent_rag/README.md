# 泰迪杯 B 题：智能问数

原 RAG Challenge 的 **PDF/表序列化/向量检索/重排/问答生成** 已**迁入本包**（`core/pdf_parser`、`llm/`、`rag/`），**不再**通过外部 `src` 转发。

## 与赛题笔记目录编号的对应

| 笔记中的名字 | 本仓库路径 |
|-------------|-----------|
| 01_data | `data/` |
| 02_core | `core/` |
| 03_agents | `agents/` |
| 04_memory | `memory/` |
| 05_rag | `rag/`（含已迁移的检索与 `generator.py`） |
| 06_pipeline | `pipeline/` |
| 07_output | `output/` |

## 已迁入的代码（原 `src/` 已删除）

| 模块 | 位置 |
|------|------|
| `pdf_parsing` | `core/pdf_parser/parser.py`（含 `JsonReportProcessor`） |
| `parsed_reports_merging` | `core/pdf_parser/utils.py`（`PageTextPreparation`） |
| `tables_serialization` | `core/pdf_parser/table_serialize.py` |
| `ingestion` | `rag/vector_store.py`（`VectorDBIngestor`, `BM25Ingestor`） |
| `retrieval` | `rag/retrieval.py` |
| `reranking` | `rag/reranking.py` |
| `text_splitter` | `rag/splitter.py` |
| `questions_processing` | `rag/generator.py`（`QuestionsProcessor`） |
| `prompts` | `llm/prompts.py` |
| `api_requests` | `llm/api_requests.py` |
| `api_request_parallel_processor` | `llm/api_request_parallel_processor.py` |

## 大模型与向量（必配）

- **智谱 GLM**：`GLM_API_KEY` 或 `ZHIPU_API_KEY`；可选 `GLM_MODEL`（如 `glm-4.7-flash`）
- **BGE 向量**（如硅基流动）：`BGE_API_KEY`；可选 `BGE_BASE_URL`、`BGE_EMBEDDING_MODEL`

本工程**不**调用 OpenAI 官方 API；`openai` 包仅作与智谱/硅基兼容的 HTTP 客户端。详见仓库根目录 `.env.example`。

## 运行

在仓库根目录：

```bash
pip install -e .
pip install -r requirements.txt
python main.py
```

或 `python -m finance_agent_rag.main`。

## 你仍需实现（赛题专用）

- `core/database/`：**建表**与 **MySQL** 已具备；任务一抽数为 **规则**（`core/extraction/rule_task1.py`），可按赛题继续调关键词与报告期推断。  
- `agents/`、`memory/`、`pipeline/task2_pipeline.py`、`task3_pipeline.py`：Text-to-SQL、多轮、澄清、出图、任务三多意图与 `references`  
- `output/`：附件7 规定的 json/xlsx/图片
