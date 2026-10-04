# Data

Everything here is produced by the scripts and committed, so results can be reproduced and checked. The files are small (a few MB).

| Path | Produced by | Contents |
|---|---|---|
| `pool/<dataset>_pool.jsonl` | `01_build_pool.py` | 300 seeded questions per dataset (screening pool) |
| `pool/<dataset>_dryrun.jsonl` | `01_build_pool.py` | First 10 pool questions, for the format check |
| `traces/dryrun/<dataset>__<model>.jsonl` | `02_generate.py --stage dryrun` | Raw dry-run traces |
| `traces/screening/<dataset>__<model>.jsonl` | `02_generate.py` | Raw screening traces (1,800 in total) |
| `traces/<stage>_scored.jsonl` | `03_score.py` | Traces plus parsed steps, prediction, `format_ok`, `answer_correct` |
| `annotation_set/selection.csv` | `04_select_annotation_set.py` | The 120 selected questions, with `k` and `partition` |
| `annotation_set/<partition>_key.csv` | `05_export_sheet.py` | Maps the opaque `trace_id` to model, item and `k`. **Don't open while annotating** |
| `annotations/` | you | Finished, validated sheets exported as CSV (`pilot_v0.csv`, `pilot_v1.csv`, `main_v1.csv`, ...) |

## Trace record fields

- **From generation:** `trace_id`, `dataset`, `task`, `item_id`, `question`, `options`, `gold`, `prompt`, `raw_output`, `n_output_tokens`, `truncated`, `model_id`, `hf_id`, `model_revision`, `prompt_version`, `decoding`, `transformers_version`, `torch_version`, `timestamp`.
- **Added by scoring:** `steps`, `final_answer_text`, `pred`, `format_ok`, `answer_correct`.
