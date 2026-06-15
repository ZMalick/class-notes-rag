// Research Assistant — Multi-Agent ADK capstone deck.
// Build: npm i pptxgenjs && node build_deck.js   (writes ./Research-Assistant-Capstone.pptx)
const pptxgen = require("pptxgenjs");

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE"; // 13.33 x 7.5
pres.author = "Zaid Malick";
pres.title = "Research Assistant — Multi-Agent Intelligence System (Google ADK)";

const W = 13.33, H = 7.5;

// ---- palette (Midnight Executive + electric accent) ----
const C = {
  navyDeep: "11162E",
  navy: "1E2761",
  ice: "CADCFC",
  panel: "F4F7FF",
  white: "FFFFFF",
  accent: "38BDF8", // electric cyan
  mint: "34D399",   // positive eval stats
  ink: "1A2233",
  mute: "64748B",
  cardLine: "E2E8F0",
};
const HEAD = "Georgia", BODY = "Calibri";

const shadow = () => ({ type: "outer", color: "1E2761", blur: 8, offset: 3, angle: 135, opacity: 0.18 });

function footer(slide, n) {
  slide.addShape(pres.shapes.RECTANGLE, { x: 0, y: 7.06, w: W, h: 0.44, fill: { color: C.navy } });
  slide.addText("Research Assistant · Multi-Agent ADK Capstone", {
    x: 0.55, y: 7.06, w: 8, h: 0.44, margin: 0, align: "left", valign: "middle",
    fontFace: BODY, fontSize: 9.5, color: C.ice,
  });
  slide.addText(String(n), {
    x: W - 1.05, y: 7.06, w: 0.5, h: 0.44, margin: 0, align: "right", valign: "middle",
    fontFace: BODY, fontSize: 9.5, color: C.ice,
  });
}

// light content slide with title + motif marker
function content(title, kicker) {
  const s = pres.addSlide();
  s.background = { color: C.white };
  s.addShape(pres.shapes.RECTANGLE, { x: 0.55, y: 0.52, w: 0.26, h: 0.26, fill: { color: C.accent } });
  s.addText(title, {
    x: 0.95, y: 0.38, w: W - 1.6, h: 0.6, margin: 0, align: "left", valign: "middle",
    fontFace: HEAD, fontSize: 28, bold: true, color: C.navy,
  });
  if (kicker) {
    s.addText(kicker, {
      x: 0.95, y: 1.0, w: W - 1.6, h: 0.4, margin: 0, align: "left", valign: "middle",
      fontFace: BODY, fontSize: 13, italic: true, color: C.mute,
    });
  }
  return s;
}

function card(s, x, y, w, h, fill) {
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, {
    x, y, w, h, rectRadius: 0.08,
    fill: { color: fill || C.panel }, line: { color: C.cardLine, width: 1 }, shadow: shadow(),
  });
}

function chip(s, x, y, w, label) {
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h: 0.42, rectRadius: 0.06, fill: { color: C.navy } });
  s.addText(label, { x, y, w, h: 0.42, margin: 0, align: "center", valign: "middle", fontFace: BODY, fontSize: 11, bold: true, color: C.white });
}

function arrow(s, x, y) {
  s.addText("→", { x, y, w: 0.5, h: 0.5, margin: 0, align: "center", valign: "middle", fontFace: BODY, fontSize: 24, bold: true, color: C.accent });
}

// ===================== Slide 1 — Title =====================
{
  const s = pres.addSlide();
  s.background = { color: C.navyDeep };
  // motif blocks
  s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 0.35, h: H, fill: { color: C.accent } });
  s.addShape(pres.shapes.RECTANGLE, { x: 0.35, y: 0, w: 0.12, h: H, fill: { color: C.navy } });
  s.addText("AGENTIC AI CAPSTONE", {
    x: 1.0, y: 1.5, w: 11, h: 0.5, margin: 0, fontFace: BODY, fontSize: 15, bold: true, color: C.accent, charSpacing: 4,
  });
  s.addText("Research Assistant", {
    x: 1.0, y: 2.05, w: 11.5, h: 1.0, margin: 0, fontFace: HEAD, fontSize: 52, bold: true, color: C.white,
  });
  s.addText("A Multi-Agent Intelligence System on Google ADK", {
    x: 1.0, y: 3.15, w: 11.5, h: 0.6, margin: 0, fontFace: BODY, fontSize: 22, color: C.ice,
  });
  s.addText("RAG over AI/ML papers + live web search, with grounded review, observability, and a live Cloud Run deployment.", {
    x: 1.0, y: 3.85, w: 10.8, h: 0.6, margin: 0, fontFace: BODY, fontSize: 14, color: C.ice,
  });
  // feature chips
  const feats = ["3 agents", "4 patterns", "RAG + web", "Evaluated", "Cloud Run"];
  const fw = 1.95, fgap = 0.22; let cx = 1.0;
  feats.forEach((f) => {
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: cx, y: 4.7, w: fw, h: 0.5, rectRadius: 0.1, fill: { color: C.navy }, line: { color: C.accent, width: 1 } });
    s.addText(f, { x: cx, y: 4.7, w: fw, h: 0.5, margin: 0, align: "center", valign: "middle", fontFace: BODY, fontSize: 12, bold: true, color: C.white });
    cx += fw + fgap;
  });
  s.addText([
    { text: "Zaid Malick", options: { bold: true, color: C.white, breakLine: true } },
    { text: "Synapse “Master Agentic AI” certification capstone", options: { color: C.ice, fontSize: 12, breakLine: true } },
    { text: "github.com/ZMalick/class-notes-rag  ·  research-assistant-969189630215.us-central1.run.app", options: { color: C.accent, fontSize: 11 } },
  ], { x: 1.0, y: 5.7, w: 11.5, h: 1.0, margin: 0, fontFace: BODY, fontSize: 14, lineSpacingMultiple: 1.1 });
}

// ===================== Slide 2 — Problem & goal =====================
{
  const s = content("The problem", "LLMs hallucinate and go stale — research answers need sources and freshness");
  // left: problem
  card(s, 0.6, 1.7, 5.9, 4.9, C.panel);
  s.addText("Why this matters", { x: 0.95, y: 1.95, w: 5.2, h: 0.4, margin: 0, fontFace: HEAD, fontSize: 18, bold: true, color: C.navy });
  s.addText([
    { text: "Language models invent plausible-but-wrong facts.", options: { bullet: true, breakLine: true } },
    { text: "Their knowledge is frozen at training cutoff — no “latest”.", options: { bullet: true, breakLine: true } },
    { text: "Research answers are only useful if they cite sources.", options: { bullet: true, breakLine: true } },
    { text: "One prompt can’t decide when to retrieve vs. search the web.", options: { bullet: true } },
  ], { x: 0.95, y: 2.5, w: 5.2, h: 3.8, margin: 0, fontFace: BODY, fontSize: 15, color: C.ink, paraSpaceAfter: 12 });
  // right: goal card (dark)
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 6.8, y: 1.7, w: 5.9, h: 4.9, rectRadius: 0.08, fill: { color: C.navy }, shadow: shadow() });
  s.addText("The goal", { x: 7.15, y: 1.95, w: 5.2, h: 0.4, margin: 0, fontFace: HEAD, fontSize: 18, bold: true, color: C.accent });
  s.addText([
    { text: "Route intelligently", options: { bold: true, color: C.white, breakLine: true } },
    { text: "between a paper corpus (RAG) and the live web.", options: { color: C.ice, breakLine: true, fontSize: 13 } },
    { text: "Verify groundedness", options: { bold: true, color: C.white, breakLine: true } },
    { text: "before any answer reaches the user.", options: { color: C.ice, breakLine: true, fontSize: 13 } },
    { text: "Measure quality", options: { bold: true, color: C.white, breakLine: true } },
    { text: "with an eval harness, and ship it live.", options: { color: C.ice, fontSize: 13 } },
  ], { x: 7.15, y: 2.55, w: 5.2, h: 3.0, margin: 0, fontFace: BODY, fontSize: 16, paraSpaceAfter: 10 });
  s.addText("Done = cited answers · smart routing · measured quality · deployed", {
    x: 7.15, y: 5.85, w: 5.2, h: 0.6, margin: 0, fontFace: BODY, fontSize: 12, italic: true, color: C.accent,
  });
  footer(s, 2);
}

// ===================== Slide 3 — Architecture =====================
{
  const s = content("Architecture", "3 Gemini agents on a deterministic control spine · state shared via ADK session");
  const cy = 2.95, bh = 1.0, by = cy - bh / 2; // common center line for the main flow
  // User query
  card(s, 0.55, by, 1.7, bh, C.panel);
  s.addText("User query", { x: 0.55, y: by, w: 1.7, h: bh, margin: 0, align: "center", valign: "middle", fontFace: BODY, fontSize: 13, bold: true, color: C.ink });
  arrow(s, 2.3, cy - 0.25);
  // Orchestrator
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 2.85, y: by, w: 2.15, h: bh, rectRadius: 0.08, fill: { color: C.navy }, shadow: shadow() });
  s.addText("Orchestrator", { x: 2.85, y: by + 0.16, w: 2.15, h: 0.4, margin: 0, align: "center", fontFace: BODY, fontSize: 14, bold: true, color: C.white });
  s.addText("routes CORPUS / WEB / BOTH", { x: 2.85, y: by + 0.55, w: 2.15, h: 0.32, margin: 0, align: "center", fontFace: BODY, fontSize: 9, color: C.ice });
  arrow(s, 5.05, cy - 0.25);
  // Loop container (centered on cy)
  const cox = 5.55, cow = 7.25, coy = 1.95, coh = 2.0; // 1.95–3.95, center 2.95
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: cox, y: coy, w: cow, h: coh, rectRadius: 0.08, fill: { color: C.panel }, line: { color: C.accent, width: 1.5 }, shadow: shadow() });
  s.addText("LoopAgent — feedback loop (max 2 iterations)", { x: cox, y: coy + 0.08, w: cow, h: 0.35, margin: 0, align: "center", fontFace: BODY, fontSize: 12, bold: true, color: C.navy });
  const iw = 1.95, ih = 0.95, iy = coy + 0.55; // 2.5–3.45
  const ix = [cox + 0.35, cox + 0.35 + iw + 0.35, cox + 0.35 + 2 * (iw + 0.35)]; // 5.9 / 8.2 / 10.5
  const inner = [["Researcher", "drafts cited answer"], ["Reviewer / QA", "groundedness check"], ["ReviewGate", "PASS → exit"]];
  inner.forEach(([t, d], i) => {
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: ix[i], y: iy, w: iw, h: ih, rectRadius: 0.06, fill: { color: C.white }, line: { color: C.cardLine, width: 1 } });
    s.addText(t, { x: ix[i], y: iy + 0.14, w: iw, h: 0.35, margin: 0, align: "center", fontFace: BODY, fontSize: 13, bold: true, color: C.navy });
    s.addText(d, { x: ix[i], y: iy + 0.5, w: iw, h: 0.32, margin: 0, align: "center", fontFace: BODY, fontSize: 9, color: C.mute });
    if (i < 2) arrow(s, ix[i] + iw - 0.06, iy + 0.22);
  });
  // tools under Researcher + FAIL caption fill the lower band
  chip(s, ix[0], 3.48, 0.95, "FAISS");
  chip(s, ix[0] + 1.0, 3.48, 0.9, "Tavily");
  s.addText("FAIL → Researcher revises (loops back)", { x: ix[1], y: 3.48, w: 4.4, h: 0.42, margin: 0, align: "left", valign: "middle", fontFace: BODY, fontSize: 10.5, italic: true, color: C.accent });
  // exit down to final answer (centered under the container)
  s.addText("↓", { x: 8.92, y: 3.96, w: 0.5, h: 0.5, margin: 0, align: "center", valign: "middle", fontFace: BODY, fontSize: 24, bold: true, color: C.accent });
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 6.6, y: 4.55, w: 5.15, h: 0.72, rectRadius: 0.08, fill: { color: C.mint }, shadow: shadow() });
  s.addText("Final cited answer", { x: 6.6, y: 4.55, w: 5.15, h: 0.72, margin: 0, align: "center", valign: "middle", fontFace: BODY, fontSize: 15, bold: true, color: C.navyDeep });
  footer(s, 3);
}

// ===================== Slide 4 — The 3 agents =====================
{
  const s = content("The three agents", "Each one job, one interface — coordinated through ADK session state");
  const agents = [
    ["O", "Orchestrator", "Classifies the query and chooses the route: CORPUS, WEB, or BOTH. Drives everything downstream."],
    ["R", "Researcher", "Calls rag_search (FAISS) and web_search (Tavily) — in parallel when needed — and drafts a cited answer."],
    ["Q", "Reviewer / QA", "Checks every claim against the retrieved evidence and emits a PASS / FAIL verdict."],
  ];
  const cw = 3.95, gap = 0.27; let x = 0.6;
  agents.forEach(([letter, name, desc]) => {
    card(s, x, 1.8, cw, 4.4, C.panel);
    s.addShape(pres.shapes.OVAL, { x: x + 0.35, y: 2.1, w: 0.9, h: 0.9, fill: { color: C.navy } });
    s.addText(letter, { x: x + 0.35, y: 2.1, w: 0.9, h: 0.9, margin: 0, align: "center", valign: "middle", fontFace: HEAD, fontSize: 28, bold: true, color: C.accent });
    s.addText(name, { x: x + 0.35, y: 3.15, w: cw - 0.7, h: 0.5, margin: 0, fontFace: HEAD, fontSize: 19, bold: true, color: C.navy });
    s.addText(desc, { x: x + 0.35, y: 3.7, w: cw - 0.7, h: 2.2, margin: 0, fontFace: BODY, fontSize: 14, color: C.ink, lineSpacingMultiple: 1.1 });
    x += cw + gap;
  });
  s.addText("ReviewGate is a tiny deterministic control node (not a 4th LLM) — it reads the verdict and exits the loop on PASS, making the stop reliable.", {
    x: 0.6, y: 6.35, w: 12.1, h: 0.5, margin: 0, align: "center", fontFace: BODY, fontSize: 12, italic: true, color: C.mute,
  });
  footer(s, 4);
}

// ===================== Slide 5 — Communication patterns =====================
{
  const s = content("Communication patterns", "Rubric requires 2+ — this system implements 4");
  const pats = [
    ["Hierarchical delegation", "The Orchestrator’s route decision drives the Researcher’s tool choice via shared session state."],
    ["Sequential flow", "A root SequentialAgent runs orchestrate → research → review in order."],
    ["Feedback loop", "Reviewer FAIL sends the draft back to the Researcher to revise (LoopAgent, max 2)."],
    ["Parallel execution", "RAG and web search fire concurrently when a query needs BOTH sources."],
  ];
  const cw = 5.9, ch = 2.15, gx = 0.31, gy = 0.3;
  const xs = [0.6, 0.6 + cw + gx], ys = [1.75, 1.75 + ch + gy];
  pats.forEach((p, i) => {
    const x = xs[i % 2], y = ys[Math.floor(i / 2)];
    card(s, x, y, cw, ch, C.panel);
    s.addShape(pres.shapes.RECTANGLE, { x, y, w: 0.12, h: ch, fill: { color: C.accent } });
    s.addText(String(i + 1), { x: x + 0.35, y: y + 0.25, w: 0.7, h: 0.7, margin: 0, fontFace: HEAD, fontSize: 30, bold: true, color: C.ice });
    s.addText(p[0], { x: x + 1.15, y: y + 0.32, w: cw - 1.4, h: 0.5, margin: 0, fontFace: HEAD, fontSize: 18, bold: true, color: C.navy });
    s.addText(p[1], { x: x + 1.15, y: y + 0.88, w: cw - 1.4, h: 1.1, margin: 0, fontFace: BODY, fontSize: 13.5, color: C.ink, lineSpacingMultiple: 1.05 });
  });
  footer(s, 5);
}

// ===================== Slide 6 — RAG pipeline =====================
{
  const s = content("RAG pipeline", "pypdf → semantic chunks → Vertex embeddings → FAISS → cited retrieval");
  const steps = ["PDF\n(pypdf)", "Chunk\n500/50 tok", "Embed\ntext-embedding-005", "FAISS\nIndexFlatIP", "Retrieve\ntop-k + cite"];
  const sw = 2.15, sh = 1.35, y = 2.05; let x = 0.6;
  steps.forEach((st, i) => {
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w: sw, h: sh, rectRadius: 0.08, fill: { color: i === steps.length - 1 ? C.navy : C.panel }, line: { color: C.cardLine, width: 1 }, shadow: shadow() });
    s.addText(st, { x, y, w: sw, h: sh, margin: 0, align: "center", valign: "middle", fontFace: BODY, fontSize: 13, bold: true, color: i === steps.length - 1 ? C.white : C.ink });
    if (i < steps.length - 1) arrow(s, x + sw - 0.02, y + 0.42);
    x += sw + 0.34;
  });
  // stat callouts (aligned to the step-row span: 0.6 → 12.71)
  const stats = [["15", "arXiv papers"], ["1,140", "chunks indexed"], ["768", "embedding dims"], ["[p.N]", "page citations"]];
  let sx = 0.6; const stw = 2.82;
  stats.forEach(([n, l]) => {
    card(s, sx, 4.1, stw, 1.95, C.panel);
    s.addText(n, { x: sx, y: 4.35, w: stw, h: 0.95, margin: 0, align: "center", valign: "middle", fontFace: HEAD, fontSize: 38, bold: true, color: C.accent });
    s.addText(l, { x: sx, y: 5.42, w: stw, h: 0.45, margin: 0, align: "center", fontFace: BODY, fontSize: 13, color: C.mute });
    sx += stw + 0.27;
  });
  footer(s, 6);
}

// ===================== Slide 7 — Routing & web search =====================
{
  const s = content("Routing & web search", "The Orchestrator picks the source — corpus, web, or both");
  const routes = [
    ["CORPUS", "Established concepts & results from the literature", "“What is scaled dot-product attention?”", C.navy],
    ["WEB", "Latest / recent / post-publication information", "“Most recent LLM releases in 2026?”", C.accent],
    ["BOTH", "Needs corpus grounding plus current context", "“How has RAG evolved to 2026?”", C.mint],
  ];
  const cw = 3.95, gap = 0.27; let x = 0.6;
  routes.forEach(([tag, desc, ex, col]) => {
    card(s, x, 1.85, cw, 3.95, C.panel);
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: x + 0.35, y: 2.15, w: 1.9, h: 0.6, rectRadius: 0.1, fill: { color: col } });
    s.addText(tag, { x: x + 0.35, y: 2.15, w: 1.9, h: 0.6, margin: 0, align: "center", valign: "middle", fontFace: BODY, fontSize: 16, bold: true, color: tag === "CORPUS" ? C.white : C.navyDeep });
    s.addText(desc, { x: x + 0.35, y: 3.0, w: cw - 0.7, h: 1.0, margin: 0, fontFace: BODY, fontSize: 14, color: C.ink, lineSpacingMultiple: 1.1 });
    s.addShape(pres.shapes.LINE, { x: x + 0.35, y: 4.15, w: cw - 0.7, h: 0, line: { color: C.cardLine, width: 1 } });
    s.addText(ex, { x: x + 0.35, y: 4.25, w: cw - 0.7, h: 1.2, margin: 0, fontFace: BODY, fontSize: 13, italic: true, color: C.navy });
    x += cw + gap;
  });
  footer(s, 7);
}

// ===================== Slide 8 — Observability =====================
{
  const s = content("Observability", "Two complementary layers — metrics for the API, traces for the eye");
  // layer 1
  card(s, 0.6, 1.8, 5.9, 2.5, C.panel);
  s.addText("1 · ObservabilityPlugin (ADK)", { x: 0.95, y: 2.05, w: 5.2, h: 0.4, margin: 0, fontFace: HEAD, fontSize: 17, bold: true, color: C.navy });
  s.addText([
    { text: "One BasePlugin on the Runner — structured JSONL per step.", options: { bullet: true, breakLine: true } },
    { text: "Per-agent latency, token counts, retrieval cosine scores.", options: { bullet: true, breakLine: true } },
    { text: "Returned in the API’s metrics dict — no external service.", options: { bullet: true } },
  ], { x: 0.95, y: 2.5, w: 5.3, h: 1.6, margin: 0, fontFace: BODY, fontSize: 13, color: C.ink, paraSpaceAfter: 8 });
  // layer 2
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.6, y: 4.45, w: 5.9, h: 2.0, rectRadius: 0.08, fill: { color: C.navy }, shadow: shadow() });
  s.addText("2 · Arize Phoenix (OpenTelemetry)", { x: 0.95, y: 4.65, w: 5.2, h: 0.4, margin: 0, fontFace: HEAD, fontSize: 17, bold: true, color: C.accent });
  s.addText([
    { text: "Flag-gated, self-hosted trace UI (localhost:6006).", options: { bullet: true, color: C.ice, breakLine: true } },
    { text: "Full agent run as a waterfall — every step, tool, token.", options: { bullet: true, color: C.ice, breakLine: true } },
    { text: "Eval-only dep — never in the production image.", options: { bullet: true, color: C.ice } },
  ], { x: 0.95, y: 5.1, w: 5.3, h: 1.2, margin: 0, fontFace: BODY, fontSize: 13, paraSpaceAfter: 6 });
  // screenshot placeholder
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 6.8, y: 1.8, w: 5.9, h: 4.65, rectRadius: 0.08, fill: { color: C.panel }, line: { color: C.accent, width: 1.5, dashType: "dash" } });
  s.addText("[ Phoenix trace screenshot ]", { x: 6.8, y: 3.7, w: 5.9, h: 0.5, margin: 0, align: "center", fontFace: BODY, fontSize: 15, bold: true, color: C.mute });
  s.addText("paste the trace waterfall captured during the demo recording", { x: 6.8, y: 4.2, w: 5.9, h: 0.5, margin: 0, align: "center", fontFace: BODY, fontSize: 11, italic: true, color: C.mute });
  footer(s, 8);
}

// ===================== Slide 9 — Evaluation =====================
{
  const s = content("Evaluation", "Ragas (Gemini 2.5 Pro judge + Vertex embeddings) over a labeled question set");
  const stats = [
    ["0.98", "Faithfulness", "answers grounded in context", C.mint],
    ["0.83", "Answer relevancy", "answers address the question", C.accent],
    ["0.81", "Context precision", "retrieved passages relevant", C.accent],
    ["0.93", "Context recall", "retrieval covers the reference", C.mint],
  ];
  const cw = 2.95, gap = 0.27; let x = 0.6;
  stats.forEach(([n, l, d, col]) => {
    card(s, x, 1.85, cw, 2.7, C.panel);
    s.addText(n, { x, y: 2.05, w: cw, h: 1.0, margin: 0, align: "center", fontFace: HEAD, fontSize: 46, bold: true, color: col });
    s.addText(l, { x, y: 3.15, w: cw, h: 0.45, margin: 0, align: "center", fontFace: BODY, fontSize: 15, bold: true, color: C.navy });
    s.addText(d, { x: x + 0.2, y: 3.62, w: cw - 0.4, h: 0.7, margin: 0, align: "center", fontFace: BODY, fontSize: 11.5, color: C.mute });
    x += cw + gap;
  });
  // routing banner
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.6, y: 4.85, w: 12.1, h: 1.55, rectRadius: 0.08, fill: { color: C.navy }, shadow: shadow() });
  s.addText("100%", { x: 0.9, y: 5.0, w: 2.6, h: 1.25, margin: 0, align: "center", valign: "middle", fontFace: HEAD, fontSize: 48, bold: true, color: C.accent });
  s.addText([
    { text: "Routing accuracy — 19 / 19", options: { bold: true, color: C.white, fontSize: 18, breakLine: true } },
    { text: "Every CORPUS / WEB / BOTH question routed correctly (deterministic check across all rows).", options: { color: C.ice, fontSize: 13 } },
  ], { x: 3.6, y: 5.0, w: 8.8, h: 1.25, margin: 0, valign: "middle", fontFace: BODY, paraSpaceAfter: 6 });
  footer(s, 9);
}

// ===================== Slide 10 — Deployment =====================
{
  const s = content("Deployment", "FastAPI → Docker → Cloud Run, built in-cloud via Cloud Build");
  const steps = ["FastAPI\n/ask · /health", "Docker\nuv from lockfile", "Cloud Build\n--source .", "Cloud Run\nlive service"];
  const sw = 2.7, sh = 1.25, y = 2.3; let x = 0.6;
  steps.forEach((st, i) => {
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w: sw, h: sh, rectRadius: 0.08, fill: { color: i === steps.length - 1 ? C.mint : C.panel }, line: { color: C.cardLine, width: 1 }, shadow: shadow() });
    s.addText(st, { x, y, w: sw, h: sh, margin: 0, align: "center", valign: "middle", fontFace: BODY, fontSize: 13, bold: true, color: i === steps.length - 1 ? C.navyDeep : C.ink });
    if (i < steps.length - 1) arrow(s, x + sw - 0.05, y + 0.37);
    x += sw + 0.36;
  });
  // detail bullets + live URL
  card(s, 0.6, 4.1, 6.0, 2.3, C.panel);
  s.addText([
    { text: "FAISS index baked into the image (no rebuild at start).", options: { bullet: true, breakLine: true } },
    { text: "Vertex/Gemini auth via the service identity — no keys in image.", options: { bullet: true, breakLine: true } },
    { text: ".gcloudignore uploads the gitignored index; secrets stay out.", options: { bullet: true, breakLine: true } },
    { text: "Public, scales to zero, max-instances capped for cost safety.", options: { bullet: true } },
  ], { x: 0.95, y: 4.35, w: 5.4, h: 1.85, margin: 0, fontFace: BODY, fontSize: 13, color: C.ink, paraSpaceAfter: 7 });
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 6.9, y: 4.1, w: 5.8, h: 2.3, rectRadius: 0.08, fill: { color: C.navy }, shadow: shadow() });
  s.addText("LIVE", { x: 7.2, y: 4.35, w: 5.2, h: 0.4, margin: 0, fontFace: BODY, fontSize: 13, bold: true, color: C.mint, charSpacing: 3 });
  s.addText("research-assistant-969189630215\n.us-central1.run.app", { x: 7.2, y: 4.8, w: 5.2, h: 1.0, margin: 0, fontFace: "Consolas", fontSize: 15, bold: true, color: C.white });
  s.addText("GET /health   ·   POST /ask { \"question\": \"…\" }", { x: 7.2, y: 5.85, w: 5.2, h: 0.4, margin: 0, fontFace: "Consolas", fontSize: 12, color: C.ice });
  footer(s, 10);
}

// ===================== Slide 11 — Decisions & challenges =====================
{
  const s = content("Key decisions & challenges", "Where engineering judgment showed up");
  const items = [
    ["Deterministic loop exit", "Replaced LLM exit_loop with a ReviewGate control node — fixed a bug where a needless second pass overwrote a good answer."],
    ["Evidence-based groundedness", "The Reviewer checks the retrieved evidence, not the draft’s claims — this caught a real hallucination during testing."],
    ["Isolated the eval stack", "Ragas needed LangChain (incompatible with v1.x) — pinned + quarantined to an eval-only group, excluded from the served app."],
  ];
  let y = 1.8;
  items.forEach(([t, d], i) => {
    card(s, 0.6, y, 12.1, 1.45, C.panel);
    s.addShape(pres.shapes.OVAL, { x: 0.9, y: y + 0.35, w: 0.75, h: 0.75, fill: { color: C.navy } });
    s.addText(String(i + 1), { x: 0.9, y: y + 0.35, w: 0.75, h: 0.75, margin: 0, align: "center", valign: "middle", fontFace: HEAD, fontSize: 24, bold: true, color: C.accent });
    s.addText(t, { x: 1.9, y: y + 0.22, w: 10.4, h: 0.5, margin: 0, fontFace: HEAD, fontSize: 18, bold: true, color: C.navy });
    s.addText(d, { x: 1.9, y: y + 0.72, w: 10.4, h: 0.6, margin: 0, fontFace: BODY, fontSize: 13.5, color: C.ink });
    y += 1.62;
  });
  footer(s, 11);
}

// ===================== Slide 12 — Rubric mapping + close =====================
{
  const s = pres.addSlide();
  s.background = { color: C.navyDeep };
  s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 0.35, h: H, fill: { color: C.accent } });
  s.addText("Rubric coverage", { x: 1.0, y: 0.55, w: 11, h: 0.7, margin: 0, fontFace: HEAD, fontSize: 30, bold: true, color: C.white });
  const hcell = (t) => ({ text: t, options: { fill: { color: C.ice }, color: C.navyDeep, bold: true, valign: "middle" } });
  const wcell = (t) => ({ text: t, options: { color: C.accent, bold: true, align: "center", valign: "middle" } });
  const bcell = (t) => ({ text: t, options: { color: C.ice, valign: "middle" } });
  const pcell = (t) => ({ text: t, options: { color: C.white, bold: true, valign: "middle" } });
  const rows = [
    [hcell("Pillar"), { text: "Weight", options: { fill: { color: C.ice }, color: C.navyDeep, bold: true, align: "center", valign: "middle" } }, hcell("Evidence")],
    [pcell("Multi-agent system (ADK)"), wcell("40%"), bcell("3 agents · 4 communication patterns · session state")],
    [pcell("Retrieval-augmented generation"), wcell("25%"), bcell("Vertex embeddings + FAISS + page-level citations")],
    [pcell("Web search"), wcell("15%"), bcell("Tavily tool + intelligent routing")],
    [pcell("Observability / deploy / presentation"), wcell("20%"), bcell("Plugin + Phoenix · Cloud Run · this deck + demo")],
  ];
  s.addTable(rows, {
    x: 1.0, y: 1.5, w: 11.3, colW: [4.8, 1.5, 5.0],
    rowH: [0.5, 0.62, 0.62, 0.62, 0.62],
    fontFace: BODY, fontSize: 14, valign: "middle",
    border: { type: "solid", pt: 1, color: C.navyDeep },
    fill: { color: C.navy },
    margin: [4, 6, 4, 6],
  });

  s.addText([
    { text: "Evaluated, observable, and live — not just a prototype.", options: { bold: true, color: C.white, fontSize: 20, breakLine: true } },
    { text: "github.com/ZMalick/class-notes-rag", options: { color: C.accent, fontSize: 14, breakLine: true } },
    { text: "research-assistant-969189630215.us-central1.run.app", options: { color: C.accent, fontSize: 14 } },
  ], { x: 1.0, y: 4.85, w: 11.3, h: 1.6, margin: 0, fontFace: BODY, lineSpacingMultiple: 1.25 });
  s.addText("Thank you", { x: 1.0, y: 6.5, w: 11, h: 0.6, margin: 0, fontFace: HEAD, fontSize: 22, bold: true, color: C.ice });
}

const OUT = "Research-Assistant-Capstone.pptx";
pres.writeFile({ fileName: OUT }).then((f) => console.log("WROTE", f)).catch((e) => { console.error("ERR", e); process.exit(1); });
