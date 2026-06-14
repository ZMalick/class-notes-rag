"""Chunks -> Vertex text-embedding-005 (768-dim) -> FAISS index on disk.

Reworked from the pre-pivot embedder: same "collect all chunks, embed, persist"
shape, but vectors come from Vertex (not local bge) and land in a FAISS
IndexFlatIP (not pgvector).

Design notes (worth narrating in the demo):
- Vectors are L2-normalized, so inner-product search (IndexFlatIP) == cosine similarity.
- Documents are embedded with task_type=RETRIEVAL_DOCUMENT and queries (in retriever.py)
  with RETRIEVAL_QUERY — asymmetric retrieval, which Vertex's embeddings are tuned for.
- FAISS stores only vectors; chunk metadata is saved alongside in chunks.json, where
  list position == the vector's id in the index.
"""
import json
from pathlib import Path

import faiss
import numpy as np
from dotenv import load_dotenv
from google import genai
from google.genai import types

from src.rag.chunker import chunk_corpus

load_dotenv()

INDEX_DIR = Path(__file__).resolve().parents[2] / "faiss_index"
MODEL = "text-embedding-005"
EMBED_DIM = 768
BATCH = 20  # texts per Vertex request (keeps each request well under the token cap)


def embed_documents(client: genai.Client, texts: list[str]) -> np.ndarray:
    """Embed corpus texts (RETRIEVAL_DOCUMENT), L2-normalized, as float32."""
    vectors: list[list[float]] = []
    cfg = types.EmbedContentConfig(task_type="RETRIEVAL_DOCUMENT", auto_truncate=True)
    for i in range(0, len(texts), BATCH):
        batch = texts[i : i + BATCH]
        resp = client.models.embed_content(model=MODEL, contents=batch, config=cfg)
        vectors.extend(e.values for e in resp.embeddings)
        print(f"  embedded {min(i + BATCH, len(texts))}/{len(texts)}")
    arr = np.asarray(vectors, dtype="float32")
    faiss.normalize_L2(arr)
    return arr


def build_index() -> None:
    chunks = chunk_corpus()
    client = genai.Client()
    print(f"\nembedding {len(chunks)} chunks via Vertex {MODEL} ...")
    vectors = embed_documents(client, [c["text"] for c in chunks])
    assert vectors.shape[1] == EMBED_DIM, f"expected {EMBED_DIM}-dim, got {vectors.shape[1]}"

    index = faiss.IndexFlatIP(EMBED_DIM)
    index.add(vectors)

    INDEX_DIR.mkdir(exist_ok=True)
    faiss.write_index(index, str(INDEX_DIR / "corpus.faiss"))
    (INDEX_DIR / "chunks.json").write_text(
        json.dumps(chunks, ensure_ascii=False), encoding="utf-8"
    )
    print(f"\nwrote {index.ntotal} vectors -> {INDEX_DIR / 'corpus.faiss'}")
    print(f"wrote {len(chunks)} chunk metas -> {INDEX_DIR / 'chunks.json'}")


if __name__ == "__main__":
    build_index()
