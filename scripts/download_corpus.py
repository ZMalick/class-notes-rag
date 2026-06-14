"""Download the pinned arXiv paper corpus into knowledge_base/.

The PDFs are gitignored; this script makes the corpus reproducible from a clean
clone. It also writes knowledge_base/manifest.json (slug -> {arxiv_id, title}) so
the chunker can attach real paper titles to chunks for citations.

Run from the project root:
    python scripts/download_corpus.py
"""
import json
import time
import urllib.error
import urllib.request
from pathlib import Path

KB = Path(__file__).resolve().parent.parent / "knowledge_base"

# (arxiv_id, filename_slug, human-readable title). Spans the rubric themes:
# transformers/attention, pretraining, RAG/retrieval, agents/tools, efficiency,
# open models, long-context. Add/remove freely — re-run to sync.
PAPERS = [
    ("1706.03762", "attention-is-all-you-need", "Attention Is All You Need"),
    ("1810.04805", "bert", "BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding"),
    ("2005.14165", "gpt-3", "Language Models are Few-Shot Learners (GPT-3)"),
    ("2005.11401", "rag", "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks"),
    ("2004.04906", "dpr", "Dense Passage Retrieval for Open-Domain Question Answering"),
    ("2201.11903", "chain-of-thought", "Chain-of-Thought Prompting Elicits Reasoning in Large Language Models"),
    ("2210.03629", "react", "ReAct: Synergizing Reasoning and Acting in Language Models"),
    ("2302.04761", "toolformer", "Toolformer: Language Models Can Teach Themselves to Use Tools"),
    ("2106.09685", "lora", "LoRA: Low-Rank Adaptation of Large Language Models"),
    ("2205.14135", "flashattention", "FlashAttention: Fast and Memory-Efficient Exact Attention with IO-Awareness"),
    ("2307.09288", "llama-2", "Llama 2: Open Foundation and Fine-Tuned Chat Models"),
    ("2310.11511", "self-rag", "Self-RAG: Learning to Retrieve, Generate, and Critique through Self-Reflection"),
    ("2212.10496", "hyde", "Precise Zero-Shot Dense Retrieval without Relevance Labels (HyDE)"),
    ("2307.03172", "lost-in-the-middle", "Lost in the Middle: How Language Models Use Long Contexts"),
    ("2401.04088", "mixtral", "Mixtral of Experts"),
]


def download(arxiv_id: str) -> bytes:
    url = f"https://arxiv.org/pdf/{arxiv_id}"
    req = urllib.request.Request(url, headers={"User-Agent": "research-assistant-capstone/0.1 (educational)"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = resp.read()
    if data[:5] != b"%PDF-":
        raise ValueError("response was not a PDF (HTML error page?)")
    return data


def main() -> None:
    KB.mkdir(exist_ok=True)
    manifest: dict[str, dict] = {}
    ok, failed = [], []

    for arxiv_id, slug, title in PAPERS:
        manifest[slug] = {"arxiv_id": arxiv_id, "title": title}
        dest = KB / f"{slug}.pdf"
        if dest.exists() and dest.stat().st_size > 0:
            print(f"skip  {slug}  (already downloaded)")
            ok.append(slug)
            continue
        try:
            data = download(arxiv_id)
            dest.write_bytes(data)
            print(f"ok    {slug:22s} {len(data) // 1024:>5} KB   <- arXiv {arxiv_id}")
            ok.append(slug)
            time.sleep(2)  # be polite to arXiv between requests
        except (urllib.error.URLError, ValueError, TimeoutError) as e:
            print(f"FAIL  {slug:22s} arXiv {arxiv_id}: {e}")
            failed.append((slug, arxiv_id, str(e)))

    (KB / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"\n{len(ok)}/{len(PAPERS)} downloaded; manifest.json written.")
    if failed:
        print("FAILURES (fix the arXiv id, then re-run):")
        for slug, aid, err in failed:
            print(f"  - {slug} ({aid}): {err}")


if __name__ == "__main__":
    main()
