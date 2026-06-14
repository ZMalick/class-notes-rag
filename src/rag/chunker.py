"""PDF -> token-windowed chunks with paper/page metadata for citations.

Salvaged from the pre-pivot transcript chunker: same sliding token-window
(CHUNK_SIZE / OVERLAP via tiktoken). What changed for the cert capstone: the
source is now PDF pages (pypdf), and each chunk carries paper title + arXiv id +
page number, so a grounded answer can cite "Title [p.N]".

Chunking is per-page: a chunk never spans two pages, which keeps page citations
exact (the trade-off is that a paragraph split across a page break is fragmented).
"""
import json
import re
from pathlib import Path

import tiktoken
from pypdf import PdfReader

KB = Path(__file__).resolve().parents[2] / "knowledge_base"

CHUNK_SIZE = 500              # tokens per chunk
OVERLAP = 50                  # tokens shared between consecutive chunks
STRIDE = CHUNK_SIZE - OVERLAP

_ENCODER = tiktoken.get_encoding("cl100k_base")


def _clean(text: str) -> str:
    """Collapse the whitespace/newline noise PDF extraction leaves behind."""
    return re.sub(r"\s+", " ", text).strip()


def _window(tokens: list[int]) -> list[list[int]]:
    """Slide a CHUNK_SIZE window across tokens, stepping by STRIDE (= overlap)."""
    windows, start = [], 0
    while start < len(tokens):
        windows.append(tokens[start : start + CHUNK_SIZE])
        start += STRIDE
    return windows


def chunk_pdf(pdf_path: Path, title: str, arxiv_id: str) -> list[dict]:
    reader = PdfReader(str(pdf_path))
    chunks: list[dict] = []
    idx = 0
    for page_num, page in enumerate(reader.pages, start=1):
        text = _clean(page.extract_text() or "")
        if len(text) < 40:  # skip near-empty pages (figures, blank)
            continue
        for window in _window(_ENCODER.encode(text)):
            chunks.append(
                {
                    "text": _ENCODER.decode(window),
                    "title": title,
                    "source": pdf_path.stem,
                    "arxiv_id": arxiv_id,
                    "page": page_num,
                    "chunk_index": idx,
                }
            )
            idx += 1
    return chunks


def chunk_corpus(kb_dir: Path = KB) -> list[dict]:
    """Chunk every PDF named in manifest.json into one flat list."""
    manifest = json.loads((kb_dir / "manifest.json").read_text(encoding="utf-8"))
    all_chunks: list[dict] = []
    for slug, meta in manifest.items():
        pdf_path = kb_dir / f"{slug}.pdf"
        if not pdf_path.exists():
            print(f"SKIP {slug}: pdf missing (run scripts/download_corpus.py)")
            continue
        chunks = chunk_pdf(pdf_path, meta["title"], meta["arxiv_id"])
        all_chunks.extend(chunks)
        print(f"{slug:24s} {len(chunks):>4} chunks")
    print(f"total: {len(all_chunks)} chunks")
    return all_chunks


if __name__ == "__main__":
    # Smoke test: chunk one paper, eyeball extraction quality + metadata.
    manifest = json.loads((KB / "manifest.json").read_text(encoding="utf-8"))
    meta = manifest["attention-is-all-you-need"]
    sample = KB / "attention-is-all-you-need.pdf"
    chunks = chunk_pdf(sample, meta["title"], meta["arxiv_id"])

    print(f"Built {len(chunks)} chunks from {sample.name}\n")
    print("--- chunk 0 metadata ---")
    print({k: v for k, v in chunks[0].items() if k != "text"})
    print("\n--- chunk 0 text (first 400 chars) ---")
    print(chunks[0]["text"][:400])
    print("\n--- chunk 5 text (first 400 chars) ---")
    print(chunks[5]["text"][:400] if len(chunks) > 5 else "(n/a)")
