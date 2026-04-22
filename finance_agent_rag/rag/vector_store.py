import os
import json
import pickle
from typing import List, Union

from pathlib import Path
from tqdm import tqdm

from dotenv import load_dotenv
from openai import OpenAI
from rank_bm25 import BM25Okapi
import faiss
import numpy as np
from tenacity import retry, wait_fixed, stop_after_attempt

from finance_agent_rag.llm.llm_env import get_embed_client, get_default_embed_model


def _l2_normalize_rows(vectors: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(vectors, axis=1, keepdims=True)
    norms = np.where(norms < 1e-12, 1.0, norms)
    return (vectors / norms).astype(np.float32)


class BM25Ingestor:
    def __init__(self):
        pass

    def create_bm25_index(self, chunks: List[str]) -> BM25Okapi:
        """Create a BM25 index from a list of text chunks."""
        tokenized_chunks = [chunk.split() for chunk in chunks]
        return BM25Okapi(tokenized_chunks)

    def process_reports(self, all_reports_dir: Path, output_dir: Path):
        """Process all reports and save individual BM25 indices.

        Args:
            all_reports_dir (Path): Directory containing the JSON report files
            output_dir (Path): Directory where to save the BM25 indices
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        all_report_paths = list(all_reports_dir.glob("*.json"))

        for report_path in tqdm(all_report_paths, desc="Processing reports for BM25"):
            # Load the report
            with open(report_path, 'r', encoding='utf-8') as f:
                report_data = json.load(f)

            # Extract text chunks and create BM25 index
            text_chunks = [chunk['text'] for chunk in report_data['content']['chunks']]
            bm25_index = self.create_bm25_index(text_chunks)

            # Save BM25 index
            sha1_name = report_data["metainfo"]["sha1_name"]
            output_file = output_dir / f"{sha1_name}.pkl"
            with open(output_file, 'wb') as f:
                pickle.dump(bm25_index, f)

        print(f"Processed {len(all_report_paths)} reports")


class VectorDBIngestor:
    def __init__(self):
        load_dotenv()
        self.llm: OpenAI = get_embed_client()
        self.embed_model = get_default_embed_model()

    @retry(wait=wait_fixed(20), stop=stop_after_attempt(2))
    def _embed_texts(self, texts: List[str], model: str) -> np.ndarray:
        if not texts:
            raise ValueError("Empty texts for embedding")
        all_vecs: List[List[float]] = []
        batch_size = int(os.environ.get("EMBEDDING_BATCH_SIZE", "16"))
        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]
            r = self.llm.embeddings.create(input=batch, model=model)
            for item in r.data:
                all_vecs.append(item.embedding)
        arr = np.array(all_vecs, dtype=np.float32)
        return _l2_normalize_rows(arr)

    def _get_embeddings(self, text: Union[str, List[str]], model: str) -> List[float]:
        """
        兼容原签名：对「字符串或字符串列表」返回扁平列表以兼容误用；正常建索引用 _embed_texts。
        若传入 str，则返回单条 embedding 的扁平 list（保持旧行为中「单条」场景）。
        """
        if isinstance(text, str) and not text.strip():
            raise ValueError("Input text cannot be an empty string.")
        m = model or self.embed_model
        if isinstance(text, str):
            r = self._embed_texts([text], m)
            return r[0].tolist()
        if isinstance(text, list):
            # 原误用: 把 list 当 char 分块; 这里按「多条文本」一批嵌入
            r = self._embed_texts(text, m)
            # 展平为一条 list[float] 仅为兼容旧 _create_vector_db 错误实现；下面 _process_report 已不走路径
            return r.flatten().tolist()
        raise TypeError(type(text))

    def _create_vector_db(self, embeddings_matrix: np.ndarray) -> "faiss.Index":
        n, d = embeddings_matrix.shape
        index = faiss.IndexFlatIP(d)
        index.add(embeddings_matrix)
        return index

    def _process_report(self, report: dict):
        text_chunks = [chunk['text'] for chunk in report['content']['chunks']]
        mat = self._embed_texts(text_chunks, self.embed_model)
        return self._create_vector_db(mat)

    def process_reports(self, all_reports_dir: Path, output_dir: Path):
        all_report_paths = list(all_reports_dir.glob("*.json"))
        output_dir.mkdir(parents=True, exist_ok=True)

        for report_path in tqdm(all_report_paths, desc="Processing reports"):
            with open(report_path, 'r', encoding='utf-8') as file:
                report_data = json.load(file)
            index = self._process_report(report_data)
            sha1_name = report_data["metainfo"]["sha1_name"]
            faiss_file_path = output_dir / f"{sha1_name}.faiss"
            faiss.write_index(index, str(faiss_file_path))

        print(f"Processed {len(all_report_paths)} reports")
