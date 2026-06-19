# Scene 6 — RAG pipeline

- **Video file:** `scene06-rag.mp4`
- **Face-cam:** OFF
- **Target:** ~2 min
- **Status:** LOCKED — drilled predict-first 2026-06-18 (the weak scene; brought back cold). Verified against `src/rag/{chunker,embedder,retriever}.py`.

## What you display
**Deck slide 6 (RAG pipeline)** — the step row (PDF → Chunk 500/50 → Embed → FAISS → Retrieve) + stat callouts (15 / 1,140 / 768 / [p.N]).
**Code cameo map (exact spots to scroll to).** Keep [src/rag/retriever.py](../../src/rag/retriever.py) open as the primary cameo; flash one line of `embedder.py` for the index type.

| Say this beat | Open this | Lines | What's on screen |
|---|---|---|---|
| Query time / cosine | [retriever.py](../../src/rag/retriever.py#L34-L51) | **L34–51** | `_embed_query()` with `faiss.normalize_L2` (**L38**), then `retrieve()`: `index.search(...)` returns `scores, ids` (**L45**) and the loop maps `ids` back to text via `chunks[idx]` (**L50**) — the index→text lookup |
| Citations | [retriever.py](../../src/rag/retriever.py#L54-L55) | **L54–55** | `citation()` → `"{title} [p.{page}]"` |
| The cosine trick (defend) | [embedder.py](../../src/rag/embedder.py#L54) | **L54** | `index = faiss.IndexFlatIP(EMBED_DIM)` — the inner-product index (pair it with `normalize_L2` at retriever **L38** / embedder **L43**) |
| Chunk size/overlap (optional) | [chunker.py](../../src/rag/chunker.py#L20-L22) | **L20–22** | `CHUNK_SIZE = 500`, `OVERLAP = 50`, `STRIDE` |
| Model + dims (optional) | [embedder.py](../../src/rag/embedder.py#L28-L29) | **L28–29** | `MODEL = "text-embedding-005"`, `EMBED_DIM = 768` |

Simplest on-camera flow: stay in **retriever.py** for the whole scene (it shows normalize + search + lookup in one view), and do a single quick jump to **embedder.py:54** when you say "inner-product index."

> **Deck fixed 2026-06-18:** slide 6 kicker now reads "500-token windows" (was "semantic chunks"). The real chunker ([src/rag/chunker.py](../../src/rag/chunker.py)) does fixed 500-token sliding windows / 50 overlap, per page. Never say "semantic" on camera — it's fixed token windows.

## What you say (LOCKED — read in your own cadence)

**Why RAG.**
> RAG is how I keep the model from hallucinating. Instead of answering from its own memory, the model answers from real pages I retrieve and hand it. The documents don't live inside the model. They live in an external index, and at query time I pull the relevant pieces and give them to the agent. That's also what makes citations possible, and it's how the system stays current instead of frozen at a training cutoff.

**Build time (indexing).**
> There are two phases. Build time is when I index the corpus. I take 15 arXiv (say "ARCHIVE") PDFs and chunk each page into 500-token windows with a 50-token overlap. The overlap keeps an idea from being cut in half at a chunk boundary, and chunking per page keeps the page citations exact. I embed every chunk with Vertex (say "VER-teks") `text-embedding-005` into a 768-dimensional vector, and I store those vectors in a FAISS (say "FACE") index. That comes out to about 1,140 chunks. Each chunk keeps its paper title and page number, and that's where the citations come from.

**Query time (retrieval).** *(show retriever.py L34–51)*
> Query time is when a question comes in. I embed the question the same way, in query mode, and FAISS ranks the stored chunks by cosine similarity, which measures how alike two passages are in meaning. FAISS hands back the integer positions of the nearest vectors. I use those positions to look up the original text, title, and page in a parallel file, `chunks.json`, where chunk number matches vector number. It returns the top five, and those passages go to the Researcher, which answers only from them. Nothing is decoded out of the vectors. The text was saved alongside them.

**The detail I defend** *(point at `normalize_L2` — retriever.py:38 / embedder.py:43 — then jump to `IndexFlatIP` at embedder.py:54).*
> Cosine similarity is the dot product of two vectors divided by both of their lengths. FAISS does a plain inner-product search, which is just the dot product. So I L2-normalize every vector to length one first. For unit vectors, dividing by the lengths does nothing, so the inner product is exactly the cosine. That means a FAISS inner-product search is mathematically identical to cosine similarity. The index is a flat, exact, brute-force search, which is instant at about 1,140 vectors.

**The tradeoff.**
> I take the top chunks by raw similarity with no reranking step, so a noisy chunk can occasionally slip into the five. That's fine at this corpus size. If precision mattered more, I'd add a reranker.

## Interview notes (say only if pushed)
- **It's a FAISS *index*, not a vector database.** I deliberately chose an on-disk index over pgvector/Pinecone: no DB server to run or deploy, and I bake the prebuilt index straight into the Cloud Run image. Tradeoff: no metadata filtering / live writes — fine for a static corpus.
- **Asymmetric retrieval:** documents are embedded with `task_type=RETRIEVAL_DOCUMENT`, the query with `RETRIEVAL_QUERY`. The model is tuned for that split, so query↔document matching is sharper.
- **"Closest" = cosine, never probability.** Cosine measures direction (the angle between vectors), which maps to alike-in-meaning. Length is ignored.

## Pronunciation cues used
arXiv = "ARCHIVE" · Vertex = "VER-teks" · FAISS = "FACE".
