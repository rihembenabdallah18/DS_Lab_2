# Notebooks

Kaggle notebooks are thin wrappers: they clone this repo, install it, and call the scripts in `scripts/`. All logic lives in `src/slm_traces/`, so the same code runs locally and on Kaggle.

| Notebook | Runs on | Purpose |
|---|---|---|
| `01_generate_traces.ipynb` | Kaggle GPU T4 ×2 | Pool → dry run → format gate → screening generation |
| `02_screening_and_selection.ipynb` | CPU | Scoring, accuracy table, stratified selection, annotation sheets |
| `03_rq1_rq2_analysis.ipynb` | CPU | Failure profiles by task and model |
| `04_rq3_automated_eval.ipynb` | Kaggle GPU + API | ProcessBench calibration, PRM and LLM judge, agreement with human labels |

*(Planned; added in the next step.)*
