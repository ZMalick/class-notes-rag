# Demo recording run-sheet

> Operational companion to [`demo-script.md`](demo-script.md). The script has the
> narration and what to point at; **this** is the do-this-in-this-order checklist
> for recording on Windows. **Method: segment-and-stitch** — record each scene of
> `demo-script.md` as its own clip, re-take fumbles, join in order in Clipchamp.
> Total target ~18–22 min across all segments (per the rewritten script). Record
> **as you lock** each scene; banked segments survive lost days before the 6/25 deadline.
>
> All commands run from the **project root** in **Git Bash** (or any shell that
> takes the `VAR=val cmd` prefix). The `PYTHONIOENCODING=utf-8` prefix stops the
> console choking on math symbols in paper text. `uv run python` and
> `.venv/Scripts/python.exe` are interchangeable — pick one and stay consistent
> on camera.

---

## A · Recording setup — OBS + segment workflow (one-time)

**Tooling:** record with **OBS Studio** (free); stitch/trim with **Clipchamp** (built
into Windows 11). OBS is the pick because the walkthrough switches between terminal,
browser (Phoenix), editor, and the live URL — single-window recorders (Game Bar) can't
follow that. Learn it once; it's reusable for every future project demo.

**OBS install + config (~4 clicks):**
1. Install from obsproject.com. First launch -> Auto-Configuration Wizard ->
   **"Optimize for recording"** (not streaming); take the defaults.
2. **Sources** box (`+`), add three:
   - **Display Capture** — the screen.
   - **Audio Input Capture** — your mic (pick the REAL device, not "default" if you
     have a headset).
   - **Video Capture Device** — your webcam; drag/resize to a bottom corner. Toggle it
     per scene with the eye icon (see face-cam plan below).
3. **Settings -> Output -> Recording Format -> `Hybrid MP4 (.mp4)`.** Crash-recoverable
   like MKV AND opens directly in Clipchamp — no remux. Do NOT pick plain
   `MPEG-4 (.mp4)` (that's the corruptible one). Set the **Recording Path** to
   `C:\Users\zaidm\Videos\research-assistant-demo\` (create it first; keep it OUT of
   the OneDrive-synced project folder so OneDrive doesn't thrash on the large files).
4. **Settings -> Video -> 1920x1080, 30 fps.**
5. **Test before the real take:** 10-sec test record -> play it back -> confirm your
   voice captured (audio meter moved while talking) and the webcam shows. The classic
   failure is narrating 20 flawless minutes into a dead mic.

**Per-scene face-cam plan** (toggle webcam visibility in OBS):

| Scene(s) | Face cam | Why |
|----------|----------|-----|
| 1 (Hook), 11 (Close) | **ON** | you're presenting / introducing yourself |
| 2 (Headline) | optional | framing — your call |
| 3–10 (architecture, code, live demo, Phoenix, eval, deploy) | **OFF** | viewers want the screen, not your face |

**File naming:** save each clip as `sceneNN-<slug>.mp4` (e.g. `scene01-hook.mp4`,
`scene06-rag.mp4`) so stitching in Clipchamp is drag-in-order.

**Audio > video.** Quiet room, a real mic (even wired earbuds) over the laptop mic.
Muddy audio sinks a walkthrough faster than a missing face cam.

---

## 0 · Pre-flight (do BEFORE you hit record)

```bash
# 1. Confirm env is live (these persist on disk; no re-setup expected)
cat .env | grep -E "GOOGLE_CLOUD_PROJECT|GOOGLE_GENAI_USE_VERTEXAI|TAVILY"   # vars present?
ls faiss_index/                                  # index built (chunks.json + .faiss)

# 2. Install eval-only deps once (needed only for the Phoenix scene)
uv sync --group eval

# 3. Warm the Cloud Run service (it scales to zero — first hit after idle is slow)
curl -s https://research-assistant-969189630215.us-central1.run.app/health

# 4. DRY RUN every query once, off-camera. Scene 4 (Reviewer FAIL) is
#    probabilistic — run the WEB query 3-4 times now and note that it CAN fail;
#    you'll capture the failing take live.
```

**Recording hygiene**
- 1080p, large terminal font (≥16pt), high-contrast theme.
- **Never show `.env`** on camera (Tavily key + project id live there).
- Clear scrollback between scenes (`clear`) so each trace starts clean.

---

## 1 · Window / terminal layout

| Window | Role | Pre-stage with |
|--------|------|----------------|
| **Terminal A** (the star, large/centered) | runs every CLI query | project root, venv active, `clear`ed |
| **Terminal B** (small, side) | Phoenix collector for Scene 6 | `phoenix serve` (start in pre-flight, leave running) |
| **Browser tab 1** | Phoenix UI | `http://localhost:6006` |
| **Browser tab 2** | the repo | `https://github.com/ZMalick/multi-agent-research-assistant` |
| **Browser tab 3** | live service | `https://research-assistant-969189630215.us-central1.run.app/health` |
| **Editor tab** | eval table | `eval/results.md` open |

Start `phoenix serve` in Terminal B during pre-flight so it's warm by Scene 6.

---

## 2 · Command sequence (map by CONTENT, not the Scene numbers below)

> NOTE: the `Scene N` labels in this block predate the 11-scene `demo-script.md`
> rewrite and do NOT line up with it (e.g. the CORPUS demo is Scene 7 in the script).
> Treat `demo-script.md` as authoritative for scene order; match these commands by
> **content** — CORPUS / WEB / FEEDBACK / BOTH / Phoenix / eval / curl — not by number.

```bash
# Scene 1 — Hook + architecture: no command. Show the README diagram / repo.

# Scene 2 — CORPUS (RAG + routing + citation)
PYTHONIOENCODING=utf-8 uv run python -m src.cli "What is scaled dot-product attention?"
#   point at: [Orchestrator] CORPUS -> rag_search -> [Attention Is All You Need p.4] -> [Reviewer] PASS -> metrics block

# Scene 3 — WEB (live search + routing)
PYTHONIOENCODING=utf-8 uv run python -m src.cli "What are the most recent large language model releases in 2026?"
#   point at: route WEB -> web_search (Tavily) -> answer with live URLs

# Scene 4 — THE FEEDBACK LOOP (the differentiator) — capture the FAIL take
PYTHONIOENCODING=utf-8 uv run python -m src.cli "What are the most recent large language model releases in 2026?"
#   re-run until you see: [Reviewer] FAIL ... -> Researcher revises -> 2nd [Reviewer] PASS
#   (this is probabilistic — keep the take where it fires)

# Scene 5 — BOTH (parallel execution)
PYTHONIOENCODING=utf-8 uv run python -m src.cli "Compare retrieval-augmented generation in the papers with the latest 2026 RAG techniques."
#   point at: route BOTH -> rag_search AND web_search -> blended answer ([p.N] + web URLs)

# Scene 6 — OBSERVABILITY (Phoenix trace) — Terminal B already running `phoenix serve`
PHOENIX_ENABLED=true PYTHONIOENCODING=utf-8 uv run python -m src.cli "How does LoRA make fine-tuning efficient?"
#   then switch to browser tab 1 (localhost:6006) -> open the trace ->
#   show the waterfall: invocation -> Orchestrator -> Researcher (rag_search) -> Reviewer -> ReviewGate
#   (this is the exact trace already captured in docs/images/phoenix-trace.png)

# Scene 7 — EVALUATION: show eval/results.md (or run routing live, no judge credit)
uv run python -m eval.run_eval --skip-ragas
#   point at: routing 19/19. Full Ragas numbers (0.98 / 0.83 / 0.81 / 0.93) are in results.md.

# Scene 8 — IT'S LIVE
curl -s https://research-assistant-969189630215.us-central1.run.app/health
#   then a real question against the cloud:
curl -s -X POST https://research-assistant-969189630215.us-central1.run.app/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What is scaled dot-product attention?"}'

# Scene 9 — Close: show the GitHub repo.
```

---

## 3 · If you want the Streamlit UI on camera instead of curl (optional)

```bash
# Terminal C
uv run python -m uvicorn src.main:app --port 8080            # API
API_URL=http://localhost:8080 uv run streamlit run app_streamlit.py   # UI -> localhost:8501
```

---

## 4 · Post-record

- [ ] Stitch the segments in order in Clipchamp; confirm the live-demo FAIL→revise
      moment (the feedback-loop take) made the cut.
- [ ] Cross-check the rubric checklist at the bottom of [`demo-script.md`](demo-script.md).
- [ ] Upload (Drive/YouTube-unlisted); paste the link into
      [`submission-post.md`](submission-post.md) (both versions).
- [ ] The Phoenix screenshot is already in the deck + README — no need to
      re-capture unless you want a different query on screen.
- [ ] Optional: take the public `/ask` endpoint private or delete the Cloud Run
      service after recording (it bills per call).
```bash
gcloud run services delete research-assistant --region us-central1     # from Git Bash
```
