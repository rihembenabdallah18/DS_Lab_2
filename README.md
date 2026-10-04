# Reasoning Failure Taxonomy for Small Language Models

A taxonomy of reasoning failures in the step-by-step traces of small language models (SLMs), built and tested on **GSM8K** (math) and **CommonsenseQA** (commonsense).

| | |
|---|---|
| **RQ1** | Which failure modes are shared across math and commonsense reasoning, and which are task-specific? |
| **RQ2** | Do different SLMs fail in different ways? |
| **RQ3** | How well do an LLM judge and a math PRM reproduce the human labels? |
| **Models** | Qwen2.5-3B-Instruct · Llama-3.2-3B-Instruct · Phi-4-mini-instruct |
| **Corpus** | 1,800 screening traces (scored automatically) → 360 annotated traces (60 shared questions per dataset × 3 models) |

The full protocol is in [`docs/project_plan.md`](docs/project_plan.md).

## Repository layout

```
docs/project_plan.md         research protocol (v2)
configs/                     every fixed choice, in one place
  models.yaml                generator and reserve models
  generation.yaml            prompt version, greedy decoding, batch size, format gate
  sampling.yaml              datasets, pool size, seed, stratum and pilot allocation
  evaluation.yaml            LLM judge and PRM settings (RQ3; filled in later)
prompts/                     versioned prompt templates (gsm8k_v1, csqa_v1)
src/slm_traces/              the code; notebooks and scripts only call into this
  data.py                    load and normalize datasets, seeded pool
  generate.py                batched, resumable generation with transformers
  parsing.py                 split responses into steps and a final answer
  scoring.py                 answer correctness and summary tables
  sampling.py                outcome-stratified selection and pilot/main split
  annotation.py              blind Excel sheets with drop-downs, label validation
scripts/                     numbered pipeline steps (see below)
annotation/
  codebook.md                how to label a trace: procedure, rules, categories
  taxonomy.yaml              category IDs (drives the drop-downs and validation)
  changelog.md               every taxonomy change, plus the hard-case list
  sheets/                    annotation sheets in progress
data/                        pool, traces, selection, finished annotations (see data/README.md)
notebooks/                   Kaggle notebooks (thin wrappers around scripts/)
results/                     tables/ and figures/
tests/                       unit tests for parsing, sampling and annotation checks
```

## Pipeline

| Step | Command | Where | Plan stage |
|---|---|---|---|
| 1 | `python scripts/01_build_pool.py` | Anywhere with internet | Draw 300 questions per dataset |
| 2a | `python scripts/02_generate.py --model <key> --stage dryrun` | Kaggle GPU | Dry run |
| 3a | `python scripts/03_score.py --stage dryrun` | Anywhere | Format gate (≥ 90% format-ok) |
| 2b | `python scripts/02_generate.py --model <key> --stage screening` | Kaggle GPU | Screening pool |
| 3b | `python scripts/03_score.py --stage screening` | Anywhere | Accuracy table |
| 4 | `python scripts/04_select_annotation_set.py` | Anywhere | Pick the 360, split pilot/main |
| 5 | `python scripts/05_export_sheet.py --partition pilot` | Anywhere | Stage B sheet (later `--partition main`) |
| 6 | `python scripts/06_validate_annotations.py annotation/sheets/pilot_sheet.xlsx` | Anywhere | Check labels after each session |

Model keys: `qwen2.5-3b`, `llama3.2-3b`, `phi4-mini` (reserve: `gemma3-4b`).

## Set-up

**Local** (scoring, selection, annotation, analysis):
```bash
pip install -e ".[dev]"
pytest
```

**Kaggle** (generation and PRM; GPU T4 ×2, internet on, phone-verified account):
```python
!git clone https://github.com/rihembenabdallah18/DS_Lab_2.git
%cd DS_Lab_2
!pip install -q -e ".[gen]"

import os
from kaggle_secrets import UserSecretsClient
os.environ["HF_TOKEN"] = UserSecretsClient().get_secret("HF_TOKEN")   # needed for Llama
```
If the repository is private, Kaggle also needs a GitHub token to clone it. The notebooks will cover this.

## Rules of the repo

- **No secrets in git.** HF tokens and API keys go in Kaggle Secrets or environment variables.
- **Configs and prompts are frozen once generation starts.** Changing them means regenerating.
- **Taxonomy changes go through [`annotation/changelog.md`](annotation/changelog.md).** Never change it mid-sheet, and never after the freeze without an agreed, logged reason.
- **Don't open `data/annotation_set/*_key.csv` while annotating.** The sheets are blind on purpose.

## Status

- [x] Protocol v2
- [x] Repository structure and pipeline code (tested)
- [ ] Supervisor sign-off on the protocol
- [ ] Hugging Face access to Llama-3.2
- [ ] Kaggle notebook: dry run and screening generation
- [ ] Stage A: taxonomy v0 from an informal read
- [ ] Stage B–D: pilot, supervisor review, freeze
- [ ] Stage E–F: main annotation and self-check
- [ ] RQ1 / RQ2 analysis
- [ ] RQ3: ProcessBench calibration, PRM, LLM judge
- [ ] Report
