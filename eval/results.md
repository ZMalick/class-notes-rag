# Evaluation results

## RAG answer quality (Ragas)

| Metric | Score |
|---|---|
| faithfulness | 0.981 |
| answer_relevancy | 0.830 |
| context_precision | 0.811 |
| context_recall | 0.933 |
| rows scored | 15 |

## Routing accuracy

**19/19 correct (100%)** — Orchestrator route vs expected.

| Expected | Actual | OK | Question |
|---|---|---|---|
| CORPUS | CORPUS | yes | What is scaled dot-product attention and why is the dot product scaled |
| CORPUS | CORPUS | yes | What two pre-training objectives does BERT use? |
| CORPUS | CORPUS | yes | What does GPT-3 demonstrate about few-shot learning? |
| CORPUS | CORPUS | yes | What are the two memory components combined in the original RAG model? |
| CORPUS | CORPUS | yes | How does Dense Passage Retrieval retrieve passages, and how does it co |
| CORPUS | CORPUS | yes | What is chain-of-thought prompting and when does it help most? |
| CORPUS | CORPUS | yes | How does ReAct differ from chain-of-thought prompting? |
| CORPUS | CORPUS | yes | How does Toolformer learn to use tools? |
| CORPUS | CORPUS | yes | What does LoRA do to make fine-tuning efficient? |
| CORPUS | CORPUS | yes | What problem does FlashAttention solve and how? |
| CORPUS | CORPUS | yes | What attention optimization does the largest Llama 2 model use for inf |
| CORPUS | CORPUS | yes | How does Self-RAG improve on standard retrieval-augmented generation? |
| CORPUS | CORPUS | yes | What is HyDE's approach to zero-shot dense retrieval? |
| CORPUS | CORPUS | yes | What did the 'Lost in the Middle' paper find about how language models |
| CORPUS | CORPUS | yes | How does Mixtral of Experts reduce the compute used per token? |
| WEB | WEB | yes | What are the most recent large language model releases in 2026? |
| WEB | WEB | yes | What are the latest developments in AI agent frameworks reported in 20 |
| BOTH | BOTH | yes | How do the attention mechanisms introduced in the original Transformer |
| BOTH | BOTH | yes | Compare retrieval-augmented generation as described in the foundationa |
