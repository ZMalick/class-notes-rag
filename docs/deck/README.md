# Capstone deck (deck-as-code)

The presentation [`../Research-Assistant-Capstone.pptx`](../Research-Assistant-Capstone.pptx)
is generated from [`build_deck.js`](build_deck.js) with [pptxgenjs](https://gitbrent.github.io/PptxGenJS/).

Rebuild:

```bash
npm install pptxgenjs
node build_deck.js   # writes Research-Assistant-Capstone.pptx
```

Open the `.pptx` in PowerPoint to refine — and paste the Phoenix trace screenshot
into slide 8 (the dashed placeholder) after recording the demo. Outline + speaker
notes live in [`../presentation-outline.md`](../presentation-outline.md).
