# Scene 10 — Deployment

- **Video file:** `scene10-deployment.mp4`
- **Face-cam:** OFF
- **Target:** ~2 min
- **Status:** LOCKED — drilled predict-first 2026-06-18. Verified against `Dockerfile` + `src/main.py`.

## What you display
1. Briefly: [Dockerfile](../../Dockerfile) and [src/main.py](../../src/main.py) (the FastAPI `/ask` + `/health` endpoints). Point at the `--no-dev` install line — that's the eval-stack exclusion.
2. Then go **live** against the cloud (Git Bash):
```bash
curl -s https://research-assistant-969189630215.us-central1.run.app/health

curl -s -X POST https://research-assistant-969189630215.us-central1.run.app/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What is scaled dot-product attention?"}'
```
3. Optional: deck slide 10 (FastAPI → Docker → Cloud Build → Cloud Run) as the visual.

## What you say (LOCKED — read in your own cadence)

**The why.**
> Right now this only runs on my laptop. For anyone else to use it, the code has to live on a computer that's always on and reachable from the internet, and my laptop is neither. So it takes three steps to get from my machine to a public URL.

**The three steps.**
> First, I wrap the agent in a FastAPI (say "Fast-A-P-I") service, with two endpoints, `/ask` and `/health`. That turns a program I run in a terminal into a service you can send a request to. Second, I package it into a Docker container: the code, its dependencies, and the prebuilt FAISS (say "FACE") index, so it runs identically anywhere. Third, I deploy that container to Google Cloud Run, which runs it on Google's always-on servers and gives back a public URL. Cloud Run builds the container in the cloud, straight from my source. A user sends a question to that URL and gets an answer. Nothing runs on their machine.

**The no-keys auth.**
> One thing worth calling out: there's no API key baked into the image. The container authenticates to Vertex (say "VER-teks") and Gemini through the Cloud Run service identity, what Google calls Application Default Credentials. Google injects the credentials at runtime, so no Google key lives in the image or in my repo. The one secret that does get passed in is the Tavily (say "TAV-ih-lee") key, handed in as a deploy-time environment variable, not baked into the image.

**Why Cloud Run.**
> I picked Cloud Run because it's serverless container hosting. I hand it a container and there's no server or VM to manage. It scales to zero when nobody's using it, so there's no cost when idle, and it scales up under load on its own.

**The tradeoff.**
> The flip side of scaling to zero is cold starts. The first request after an idle stretch is slow, because the container has to spin up from nothing. I capped max-instances for cost safety. That's fine for a demo; a high-traffic app would keep one instance warm.

**What ships and what doesn't.**
> Worth pointing at the Dockerfile. The prebuilt FAISS index ships inside the image, so retrieval has no external database to call. The corpus PDFs don't ship, only the index does. And the dev and eval tools, Ragas and Phoenix, are excluded with a no-dev install, so the trace UI I showed in Scene 8 is never in the production container.

**Live.**
> Here it is answering live in the cloud.
> (run the `/health` curl, then the `/ask` curl)

## Interview notes (say only if pushed)
- **The two endpoints, precisely:** `/health` is a GET returning `{"status": "ok"}` with **no model calls** — a liveness probe Cloud Run hits to check the box is up. `/ask` is a POST `{question}` returning `{question, answer, route, review_verdict, metrics}`, running the **same `root_agent` the CLI runs**.
- **Why no-keys matters:** if the image leaked, no Google credentials leak with it. ADC ties auth to the service account, not a string in the repo.
- **Secondary Cloud Run tradeoff:** it ties the deploy to GCP's identity model — simplest and most secure on Google, but not portable to another cloud without rework.
- **Build path:** `gcloud run deploy --source .` → Cloud Build builds the image from the root `Dockerfile` (`deployment/Dockerfile` is the local `docker build -f` equivalent).
- **The `--no-dev` line is the proof:** it's the literal mechanism behind the Scene 8 claim that Phoenix/Ragas never enter production.
- **Live URL:** `research-assistant-969189630215.us-central1.run.app`.

## Pronunciation cues used
FastAPI = "Fast-A-P-I" · FAISS = "FACE" · Vertex = "VER-teks" · Tavily = "TAV-ih-lee" · Gemini = "JEM-in-eye".
