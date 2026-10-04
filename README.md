# Reasoning Failure Taxonomy for Small Language Models

A taxonomy of reasoning failures in the step-by-step answers ("traces") of small language models, built from **GSM8K** (math) and **CommonsenseQA** (commonsense).

- **RQ1:** Which failure modes are shared across math and commonsense reasoning, and which are task-specific?
- **RQ2:** Do different small models fail in different ways?
- **RQ3:** How well can automated evaluators reproduce the human labels?

**Models:** Qwen2.5-3B-Instruct · Llama-3.2-3B-Instruct · Phi-4-mini-instruct

The full plan is in [`docs/project_plan.md`](docs/project_plan.md).

## Current step

**Step 1: generate the traces.** Run the 3 models on questions from both datasets (on Kaggle), check the final answers automatically, and save the traces.
