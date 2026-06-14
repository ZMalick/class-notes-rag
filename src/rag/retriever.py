"""Query -> Vertex query-embedding -> FAISS top-k chunks with citations.

Reworked from the pre-pivot Shape-A retriever (which only embedded the query):
now it loads the persisted FAISS index + chunk metadata, embeds the query with
task_type=RETRIEVAL_QUERY (matching the corpus's RETRIEVAL_DOCUMENT side), runs
top-k inner-product (== cosine, since vectors are normalized) search, and returns
chunks with their citations.
"""
import json
from functools import lru_cache
from pathlib import Path

import faiss
import numpy as np
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

INDEX_DIR = Path(__file__).resolve().parents[2] / "faiss_index"
MODEL = "text-embedding-005"


@lru_cache(maxsize=1)
def _load():
    """Load index + metadata + client once (cached for the process)."""
    index = faiss.read_index(str(INDEX_DIR / "corpus.faiss"))
    chunks = json.loads((INDEX_DIR / "chunks.json").read_text(encoding="utf-8"))
    client = genai.Client()
    return index, chunks, client


def _embed_query(client: genai.Client, query: str) -> np.ndarray:
    cfg = types.EmbedContentConfig(task_type="RETRIEVAL_QUERY", auto_truncate=True)
    resp = client.models.embed_content(model=MODEL, contents=[query], config=cfg)
    arr = np.asarray([resp.embeddings[0].values], dtype="float32")
    faiss.normalize_L2(arr)
    return arr


def retrieve(query: str, k: int = 5) -> list[dict]:
    """Return the top-k corpus chunks for a query, each with a cosine score."""
    index, chunks, client = _load()
    scores, ids = index.search(_embed_query(client, query), k)
    results = []
    for score, idx in zip(scores[0], ids[0]):
        if idx == -1:  # FAISS pads with -1 when fewer than k results exist
            continue
        results.append({**chunks[idx], "score": float(score)})
    return results


def citation(chunk: dict) -> str:
    return f"{chunk['title']} [p.{chunk['page']}]"


if __name__ == "__main__":
    queries = [
        "What is scaled dot-product attention?",
        "How does retrieval-augmented generation reduce hallucination?",
        "What is low-rank adaptation (LoRA) for fine-tuning?",
        "How does ReAct combine reasoning and acting?",
        "Why do language models struggle with information in the middle of long contexts?",
    ]
    for q in queries:
        print(f"\n=== {q}")
        for r in retrieve(q, k=3):
            print(f"  [{r['score']:.3f}] {citation(r)}  ({r['source']})")
            print(f"        {r['text'][:130].strip()}...")
