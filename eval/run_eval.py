"""Ragas evaluation harness for the multi-agent Research Assistant.

What it measures:
  1. RAG answer quality — for every labeled CORPUS/BOTH question (those with a
     reference answer), four Ragas metrics scored by a Gemini judge + Vertex
     embeddings:
       - faithfulness        : is the answer grounded in the retrieved context?
       - answer_relevancy    : does the answer actually address the question?
       - context_precision   : are the retrieved passages relevant (ranked well)?
       - context_recall      : did retrieval surface what the reference needs?
  2. Routing accuracy — across ALL rows (incl. WEB/BOTH), does the Orchestrator's
     route match the expected route? This is deterministic (no judge), so it's
     free and covers the routes Ragas can't (live-web answers have no stable
     reference to score against).

Why this split: Ragas' reference-based metrics need a fixed ground-truth answer,
which only the static corpus provides. Web answers change, so we grade their
*routing* rather than their content.

Cost: one full multi-agent run per question + ~4 judge calls per scored row.
Use --limit for a cheap smoke before committing to the full set.

Run from the project root (eval deps: `uv sync --group eval`):
    PYTHONIOENCODING=utf-8 .venv/Scripts/python.exe -m eval.run_eval              # full set
    PYTHONIOENCODING=utf-8 .venv/Scripts/python.exe -m eval.run_eval --limit 1    # smoke (1 row)
    PYTHONIOENCODING=utf-8 .venv/Scripts/python.exe -m eval.run_eval --skip-ragas # pipeline + routing only (no judge credit)
"""
import argparse
import asyncio
import json
import os
import warnings
from pathlib import Path

from dotenv import load_dotenv

# The legacy ragas metric singletons warn on import (they live until v1.0);
# silence the noise so the report reads cleanly.
warnings.filterwarnings("ignore", category=DeprecationWarning)
# Skip ragas' usage analytics (avoids a background network call).
os.environ.setdefault("RAGAS_DO_NOT_TRACK", "true")

load_dotenv()

HERE = Path(__file__).resolve().parent
DATASET = HERE / "dataset.jsonl"
RESULTS = HERE / "results.md"

JUDGE_MODEL = os.getenv("JUDGE_MODEL", "gemini-2.5-pro")
EMBED_MODEL = os.getenv("EMBED_MODEL", "text-embedding-005")


def load_dataset(limit: int | None = None) -> list[dict]:
    rows = []
    with DATASET.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows[:limit] if limit else rows


async def collect_runs(rows: list[dict]) -> list[dict]:
    """Run each question through the full pipeline; capture answer/route/contexts."""
    from src.pipeline import run_query

    out = []
    for i, row in enumerate(rows):
        q = row["question"]
        print(f"  [{i + 1}/{len(rows)}] {row.get('expected_route', '?'):6} | {q[:64]}")
        result = await run_query(q, session_id=f"eval-{i}")
        contexts = [
            c.get("text", "")
            for c in (result.get("retrieved_context") or [])
            if c.get("text")
        ]
        out.append(
            {
                **row,
                "answer": result.get("answer") or "",
                "actual_route": result.get("route"),
                "contexts": contexts,
            }
        )
    return out


def routing_report(runs: list[dict]) -> tuple[int, int, list[dict]]:
    """Compare expected vs actual route over rows that declare an expected route."""
    judged = [r for r in runs if r.get("expected_route")]
    detail = [
        {
            "question": r["question"],
            "expected": r["expected_route"].upper(),
            "actual": (r.get("actual_route") or "NONE").upper(),
            "ok": (r.get("actual_route") or "").upper() == r["expected_route"].upper(),
        }
        for r in judged
    ]
    correct = sum(1 for d in detail if d["ok"])
    return correct, len(judged), detail


def run_ragas(runs: list[dict]):
    """Score the reference-bearing rows with the four Ragas RAG metrics."""
    from langchain_google_vertexai import ChatVertexAI, VertexAIEmbeddings
    from ragas import EvaluationDataset, evaluate
    from ragas.dataset_schema import SingleTurnSample
    from ragas.embeddings import LangchainEmbeddingsWrapper
    from ragas.llms import LangchainLLMWrapper
    from ragas.metrics import (
        answer_relevancy,
        context_precision,
        context_recall,
        faithfulness,
    )

    project = os.environ["GOOGLE_CLOUD_PROJECT"]
    location = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")

    judge = LangchainLLMWrapper(
        ChatVertexAI(model=JUDGE_MODEL, temperature=0.0, project=project, location=location)
    )
    embeddings = LangchainEmbeddingsWrapper(
        VertexAIEmbeddings(model_name=EMBED_MODEL, project=project, location=location)
    )

    scored = [r for r in runs if r.get("ground_truth") and r.get("contexts")]
    if not scored:
        print("  (no reference-bearing rows with retrieved context — skipping Ragas)")
        return None

    samples = [
        SingleTurnSample(
            user_input=r["question"],
            response=r["answer"],
            retrieved_contexts=r["contexts"],
            reference=r["ground_truth"],
        )
        for r in scored
    ]
    dataset = EvaluationDataset(samples=samples)
    metrics = [faithfulness, answer_relevancy, context_precision, context_recall]
    print(f"  scoring {len(scored)} rows x {len(metrics)} metrics with judge={JUDGE_MODEL} ...")
    return evaluate(dataset, metrics=metrics, llm=judge, embeddings=embeddings)


def write_results(runs, routing, ragas_result) -> None:
    correct, total, detail = routing
    lines = ["# Evaluation results", ""]

    lines.append("## RAG answer quality (Ragas)")
    lines.append("")
    if ragas_result is not None:
        df = ragas_result.to_pandas()
        means = df.select_dtypes("number").mean()
        lines.append("| Metric | Score |")
        lines.append("|---|---|")
        for name, val in means.items():
            lines.append(f"| {name} | {val:.3f} |")
        lines.append(f"| rows scored | {len(df)} |")
    else:
        lines.append("_Not run (use without --skip-ragas to score)._")
    lines.append("")

    lines.append("## Routing accuracy")
    lines.append("")
    pct = (correct / total) if total else 0.0
    lines.append(f"**{correct}/{total} correct ({pct:.0%})** — Orchestrator route vs expected.")
    lines.append("")
    lines.append("| Expected | Actual | OK | Question |")
    lines.append("|---|---|---|---|")
    for d in detail:
        mark = "yes" if d["ok"] else "NO"
        lines.append(f"| {d['expected']} | {d['actual']} | {mark} | {d['question'][:70]} |")
    lines.append("")

    RESULTS.write_text("\n".join(lines), encoding="utf-8")
    print(f"\nWrote {RESULTS}")


def main() -> None:
    ap = argparse.ArgumentParser(description="Ragas + routing evaluation harness.")
    ap.add_argument("--limit", type=int, default=None, help="only run the first N rows (smoke test)")
    ap.add_argument("--skip-ragas", action="store_true", help="pipeline + routing only (no judge credit)")
    args = ap.parse_args()

    rows = load_dataset(limit=args.limit)
    print(f"Loaded {len(rows)} eval rows from {DATASET.name}\n--- running pipeline ---")
    runs = asyncio.run(collect_runs(rows))

    routing = routing_report(runs)
    correct, total, _ = routing
    print(f"\n--- routing accuracy: {correct}/{total} ---")

    ragas_result = None
    if not args.skip_ragas:
        print("\n--- Ragas scoring ---")
        ragas_result = run_ragas(runs)
        if ragas_result is not None:
            print("\n" + str(ragas_result))

    write_results(runs, routing, ragas_result)


if __name__ == "__main__":
    main()
