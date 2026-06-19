# Scene 9 — Evaluation

- **Video file:** `scene09-evaluation.mp4`
- **Face-cam:** OFF
- **Target:** ~2 min
- **Status:** LOCKED — drilled predict-first 2026-06-18. Verified against `eval/{run_eval.py, results.md, dataset.jsonl}`.

## What you display
1. [eval/results.md](../../eval/results.md) open — the real Ragas numbers + the 19/19 routing table.
2. Optionally deck slide 9 (the four stat cards + the 100% routing banner) as the cleaner visual.
3. Optional live: the deterministic routing check (no judge credit spent):
```bash
uv run python -m eval.run_eval --skip-ragas
```

## What you say (LOCKED — read in your own cadence)

**The problem.**
> I didn't want to just eyeball this and say it looks right. The hard part is that the output is prose. There's no single correct string to assert against, because the same correct answer can be written a hundred different ways. So normal exact-match testing is useless on the answer itself.

**The fix: LLM-as-judge.**
> So I use LLM-as-judge. A separate, stronger model reads the question, the answer, and the evidence that was retrieved, and it scores the answer from 0 to 1 on specific criteria. The library that runs that is Ragas (say "RAH-guss").

**The split (this is the beat that matters).**
> Two things get measured, over two different sets of questions. Ragas grades answer quality on the 15 corpus questions, because only those have a fixed reference answer to grade against. The 2 web and 2 mixed questions have no stable reference. What's the latest model in 2026 changes month to month, so there's nothing fixed to score their content against. For those I grade the one thing that is stable, which is routing. Routing accuracy runs over all 19 questions, because checking the route is just an exact match against the route I expected. It needs no reference answer, so it covers every row. That came out 19 out of 19.

**The four metrics.**
> Ragas gives me four numbers. Two grade the answer, two grade the retrieval. On the answer side: faithfulness, which is whether every claim is grounded in the retrieved context, and that's the same check my Reviewer agent runs live, just scored as a number. That's 0.98, my highest, which is exactly the point of the system. And answer relevancy, whether the answer actually addresses the question, at 0.83. On the retrieval side: context precision, whether what I retrieved was relevant, at 0.81, and context recall, whether retrieval surfaced everything the reference needed, at 0.93.

**The judge.**
> The judge is Gemini (say "JEM-in-eye") 2.5 Pro. The agents themselves run on Flash. The judge should be at least as capable as the thing it's grading, and Pro is the stronger model. I can afford Pro here because eval runs offline and occasionally, so latency and cost don't matter the way they do for the live agents, where Flash's speed wins on every request.

**The tradeoff.**
> The honest weakness is that using an LLM to grade an LLM is a bit circular. I'm trusting a model to tell me a model did well. Three things keep it honest: the judge is stronger than what it grades, the prompts are narrow and per-metric, asking whether one specific claim is supported by one specific piece of context rather than a vague "is this good," and I average over many questions so one bad grade doesn't swing the result.

**Closer.**
> So I can put real numbers on the quality instead of taking my own word for it.

## Interview notes (say only if pushed)
- **The split, precisely (the literal code):** routing-eligible = any row with an `expected_route` (all 19). Ragas-eligible = a row with a `ground_truth` reference **and** retrieved context (the 15 corpus rows). The 4 web/mixed rows carry `ground_truth: null`.
- **Doc caveat — do NOT repeat on camera:** `run_eval.py`'s docstring says Ragas scores "CORPUS/BOTH" questions. That's stale for this dataset — the BOTH rows are null, so it's **15 corpus only**. Always say "15 corpus questions," never "corpus and both."
- **Faithfulness is groundedness, not truth.** Grounded-in-its-sources, not true-in-the-world. Same honesty point as Scenes 7 and 8: if a web page is wrong, a faithfully-cited answer can still be wrong.
- **Precision vs recall shape:** high recall (0.93) with slightly lower precision (0.81) = retrieval grabbed the right material plus a little noise. That's the normal top-k-without-reranking profile I flagged in Scene 6.
- **Ragas uses embeddings too:** the embedding-based parts (answer relevancy) run on Vertex `text-embedding-005`; the *judging* is Pro. Two model roles inside the eval, same as the system.
- **Numbers source (verified this session):** `eval/results.md` — faithfulness 0.981, answer_relevancy 0.830, context_precision 0.811, context_recall 0.933, rows scored 15; routing 19/19 (100%). Deck slide 9 = the same four cards + the routing banner.

## Pronunciation cues used
Ragas = "RAH-guss" · Gemini = "JEM-in-eye".
