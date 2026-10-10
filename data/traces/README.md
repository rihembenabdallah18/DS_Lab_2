# Traces

Trace files saved by `notebooks/01_generate_traces.ipynb`. Each line is one trace: the question, the correct answer, the model's full answer, its steps, its final answer and whether it is correct.

| Folder | Prompt | Used for |
|---|---|---|
| `v1/` | v1 (original) | The 42-trace pilot (`annotation/stage_a/`) that builds the taxonomy |
| this folder | v2: adds "In the last step, state the result you have reached" (math) / "state which option you choose and why" (commonsense) | Everything after the pilot: main annotation and analysis |

Upload the v2 files here. File names, as the notebook saves them: `traces_<model>_<questions per dataset>_v2.jsonl`, for example
- `traces_qwen2.5-3b_300_v2.jsonl`
- `traces_llama3.2-3b_300_v2.jsonl`
- `traces_phi4-mini_300_v2.jsonl`

**Why v2:** with v1, many commonsense traces compared the options but never stated which one they chose, leaving the decision to the `Final answer:` line (roughly 45% of Llama's, 63% of Qwen's and 83% of Phi's traces, by a rough keyword check). This was equally common for right and wrong answers, so it is a writing style encouraged by the prompt, not a reasoning failure. All 1,800 traces are regenerated with v2, rather than only the affected ones, so every model and question uses the same prompt.
