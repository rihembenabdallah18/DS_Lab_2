# Traces

Upload the trace files saved by `notebooks/01_generate_traces.ipynb` here.

File names, as the notebook saves them: `traces_<model>_<questions per dataset>.jsonl`, for example
- `traces_qwen2.5-3b_300.jsonl`
- `traces_llama3.2-3b_300.jsonl`
- `traces_phi4-mini_300.jsonl`

Each line is one trace: the question, the correct answer, the model's full answer, its steps, its final answer and whether it is correct.
