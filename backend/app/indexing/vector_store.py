import os
import json
import math
import numpy as np
from typing import List, Dict, Any, Optional
from rank_bm25 import BM25Okapi
from google import genai
from ..core.config import settings
from .chunker import CodeChunk

class HybridVectorStore:
    """Zero-docker hybrid retrieval engine: BM25 + Gemini Embeddings + Local Cache + RRF."""

    def __init__(self, cache_dir: str = ".codenexus_cache"):
        self.cache_dir = cache_dir
        self.chunks: List[CodeChunk] = []
        self.embeddings: List[List[float]] = []
        self.bm25: Optional[BM25Okapi] = None
        self.corpus_tokens: List[List[str]] = []
        self.embedding_cache: Dict[str, List[float]] = {}
        self.client: Optional[genai.Client] = None
        self._init_client()
        self._load_cache()

    def _init_client(self):
        api_key = settings.GEMINI_API_KEY or os.environ.get("GEMINI_API_KEY")
        if api_key:
            try:
                self.client = genai.Client(api_key=api_key)
            except Exception:
                self.client = None

    def _load_cache(self):
        os.makedirs(self.cache_dir, exist_ok=True)
        cache_file = os.path.join(self.cache_dir, "embeddings.json")
        if os.path.isfile(cache_file):
            try:
                with open(cache_file, "r", encoding="utf-8") as f:
                    self.embedding_cache = json.load(f)
            except Exception:
                self.embedding_cache = {}

    def _save_cache(self):
        os.makedirs(self.cache_dir, exist_ok=True)
        cache_file = os.path.join(self.cache_dir, "embeddings.json")
        try:
            with open(cache_file, "w", encoding="utf-8") as f:
                json.dump(self.embedding_cache, f)
        except Exception:
            pass

    def index_chunks(self, chunks: List[CodeChunk]):
        self.chunks = chunks
        self.corpus_tokens = [c.content.lower().split() for c in chunks]
        if self.corpus_tokens:
            self.bm25 = BM25Okapi(self.corpus_tokens)

        # Generate or load embeddings
        self.embeddings = []
        uncached_chunks = []
        uncached_indices = []

        for idx, chunk in enumerate(chunks):
            if chunk.chunk_id in self.embedding_cache:
                self.embeddings.append(self.embedding_cache[chunk.chunk_id])
            else:
                self.embeddings.append([])
                uncached_chunks.append(chunk)
                uncached_indices.append(idx)

        # Batch embed uncached chunks if Gemini client available
        if self.client and uncached_chunks:
            try:
                batch_size = 50
                for i in range(0, len(uncached_chunks), batch_size):
                    batch = uncached_chunks[i : i + batch_size]
                    texts = [c.content for c in batch]
                    res = self.client.models.embed_content(
                        model=settings.EMBEDDING_MODEL,
                        contents=texts
                    )
                    # Extract embeddings
                    for item_idx, emb in enumerate(res.embeddings):
                        orig_idx = uncached_indices[i + item_idx]
                        values = list(emb.values)
                        self.embeddings[orig_idx] = values
                        self.embedding_cache[chunks[orig_idx].chunk_id] = values
                self._save_cache()
            except Exception as e:
                print(f"[CodeNexus] Embedding error or API limit: {e}")

    def hybrid_search(self, query: str, top_k: int = 6) -> List[Dict[str, Any]]:
        if not self.chunks:
            return []

        # 1. Lexical Search (BM25)
        query_tokens = query.lower().split()
        bm25_scores = self.bm25.get_scores(query_tokens) if self.bm25 else [0.0] * len(self.chunks)
        bm25_ranks = np.argsort(bm25_scores)[::-1]

        # 2. Vector Search (if embeddings available)
        dense_ranks = []
        if self.client and any(self.embeddings):
            try:
                q_res = self.client.models.embed_content(
                    model=settings.EMBEDDING_MODEL,
                    contents=query
                )
                q_vec = np.array(q_res.embeddings[0].values)
                
                # Compute cosine similarities
                sims = []
                for emb in self.embeddings:
                    if emb:
                        v = np.array(emb)
                        denom = (np.linalg.norm(q_vec) * np.linalg.norm(v))
                        sim = float(np.dot(q_vec, v) / denom) if denom > 0 else 0.0
                        sims.append(sim)
                    else:
                        sims.append(0.0)
                dense_ranks = np.argsort(sims)[::-1]
            except Exception:
                dense_ranks = []

        # 3. Reciprocal Rank Fusion (RRF)
        rrf_scores: Dict[int, float] = {}
        for rank, doc_idx in enumerate(bm25_ranks[:50]):
            rrf_scores[doc_idx] = rrf_scores.get(doc_idx, 0.0) + (1.0 / (60.0 + rank + 1))

        if len(dense_ranks) > 0:
            for rank, doc_idx in enumerate(dense_ranks[:50]):
                rrf_scores[doc_idx] = rrf_scores.get(doc_idx, 0.0) + (1.0 / (60.0 + rank + 1))

        # Sort combined
        sorted_indices = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)[:top_k]

        results = []
        for idx, score in sorted_indices:
            chunk = self.chunks[idx]
            results.append({
                "chunk": chunk.to_dict(),
                "score": round(float(score), 4),
                "file_path": chunk.file_path,
                "lines": f"{chunk.start_line}-{chunk.end_line}",
                "symbol": chunk.symbol_name
            })
        return results
