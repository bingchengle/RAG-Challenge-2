# 财报「智能问数」工程（泰迪杯 B 题）

本仓库在 [RAG Challenge 2](https://github.com/IlyaRice/RAG-Challenge-2) 的 PDF/RAG/LLM 实现基础上，**重组为**赛题用包 **`finance_agent_rag/`**；原根目录的 `src/` 与 RAG 赛 `pipeline` **已移除**，解析与检索逻辑已**迁入**该包内。

- **赛题实现说明与目录**：见 [`finance_agent_rag/README.md`](finance_agent_rag/README.md)  
- **样例数据**（原竞赛）：仍位于 `data/test_set/`、`data/erc2_set/`，可配合 `core/pdf_parser` 做解析与建库试验

## 安装与入口

```bash
pip install -e .
pip install -r requirements.txt
python main.py
```

大模型：在 `.env` 或系统环境变量中配置 **智谱 `GLM_API_KEY`（或 `ZHIPU_API_KEY`）** 与 **`BGE_API_KEY`**（见 `.env.example`）；**不**使用 OpenAI 官方 API。依赖见 `requirements.txt`。

## License

继承原仓库（MIT 等，见 `LICENSE`）。
