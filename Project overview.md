# Project Plan (v2): A Unified Reasoning Failure Taxonomy for Small Language Models in QA

> **Status:** revised draft for supervisor review. Items marked **[CONFIRM]** are open decisions (collected in the last section).

## What changed from v1

| Area | v1 | v2 | Why |
|---|---|---|---|
| Sampling | 75 random questions per dataset | Run all models on a larger **screening pool** (300 questions per dataset), then pick 75 **shared** questions per dataset, **stratified by how many models got each one wrong** | 3–4B models answer most GSM8K/CSQA questions correctly. A random 75 would give too few failures per model to build or compare categories |
| Models | "About three SLMs" | Qwen2.5-3B-Instruct, Llama-3.2-3B-Instruct, Phi-4-mini-instruct | These are the same families ReTraceQA used, at matched size, which keeps the commonsense results comparable |
| Splits | Unspecified | GSM8K **test** (1,319); CommonsenseQA **validation** (1,221) | CommonsenseQA test answers are not public |
| Automated evaluation | Unspecified judge; PRM-7B | Free-tier API judge from a family **not** among the generators; PRM run on a free GPU notebook, with a smaller fallback PRM | The project has no budget for paid APIs or GPUs |
| Calibration | None | Sanity-check the PRM and judge set-up on ProcessBench's GSM8K subset (human labels) before using them on our data | Separates "our pipeline is broken" from "the evaluator disagrees with us" |
| Reliability | Supervisor qualitative review only | Plus a re-annotation of ~10% by the same annotator after a time gap, and an optional 30-trace supervisor double-label | Cheap evidence of label stability without a full multi-annotator study |
| Reporting | Raw frequencies | Rates over the whole screening pool, failure-mode profiles within strata (reweighted where needed) | Stratified sampling deliberately over-represents failures, so raw frequencies would be biased |

## 1. Objective and research questions

Build and empirically test a hierarchical taxonomy of failures in the **observable** step-by-step reasoning traces of instruction-tuned SLMs, on math (GSM8K) and commonsense (CommonsenseQA) QA. The project makes no claims about hidden internal reasoning.

- **RQ1 (primary):** Which failure modes are shared across math and commonsense reasoning, and which are task-specific?
- **RQ2:** Do different SLMs show different failure profiles, or a common one across tasks?
- **RQ3:** How well do automated evaluators (one general LLM judge and one math PRM) reproduce the human labels?

The order is fixed, RQ1 → RQ2 → RQ3. RQ1 produces the codebook and the reference labels that RQ2 and RQ3 depend on.

**Out of scope:** training a PRM or classifier, domains beyond the two datasets, a large panel of judges, a full multi-annotator reliability study.

## 2. Grounding in prior work

**ReTraceQA** (Molfese et al., ACL 2026) is the commonsense anchor.
- Seven instruction-tuned SLMs (Llama 3.2/3.1, Qwen2.5, Phi-4-mini) generated zero-shot CoT traces on CSQA, OBQA, QASC and StrategyQA.
- 2,421 traces were expert-annotated with the first error step and an error type: **Misinterpretation** (misreading the question or options), **Hallucination** (false or unverifiable world knowledge) or **Reasoning** (invalid inference).
- 14–24% of correct answers came with flawed reasoning, and reasoning-aware scoring lowered SLM scores by up to 25 points.
- *Taken over:* trace validity separate from answer correctness, first-error localisation, and the three error types as **seed parent categories** to test, not to adopt.

**ProcessBench** (Zheng et al., ACL 2025) is the math anchor.
- 3,400 solutions across GSM8K, MATH, OlympiadBench and Omni-MATH, each labelled with the **earliest erroneous step** (or "no error").
- Process errors among correct-answer solutions are rare on GSM8K (≈3.5%) and common on harder sets. Errors cluster in early steps.
- *Metric:* F1 = harmonic mean of accuracy on erroneous and on error-free solutions.
- Qwen2.5-Math-PRM-7B is reported at ≈82 F1 on the GSM8K subset, which is competitive with GPT-4o used as a critic.
- *Taken over:* the earliest-error definition, the F1 metric for RQ3, and the GSM8K subset as a calibration set.

**What this means for v2:**
1. Math traces with a correct answer but flawed reasoning will be rare. Most math failures will come from wrong-answer traces, which is another reason to stratify by outcome.
2. Using ReTraceQA's model families makes our CSQA findings directly comparable to theirs.

## 3. Datasets

| Task | Dataset | Split used | Size | Answer check |
|---|---|---|---|---|
| Math | GSM8K | test | 1,319 | Last number after `Final answer:` compared numerically with the gold answer |
| Commonsense | CommonsenseQA | validation | 1,221 (5 options) | Option letter after `Final answer:` compared with the gold letter |

Caveats to state in the report:
- With one dataset per task, "task-specific" means *specific to these datasets*.
- Both benchmarks are public and may appear in the models' training data. This affects accuracy more than the structure of failures, but it should be acknowledged.

## 4. Model selection

| Role | Model | Size | Reason |
|---|---|---|---|
| Generator 1 | Qwen2.5-3B-Instruct | 3B | Used in ReTraceQA; strong for its size; reliable instruction following |
| Generator 2 | Llama-3.2-3B-Instruct | 3B | Used in ReTraceQA; different family and training data |
| Generator 3 | Phi-4-mini-instruct | 3.8B | Used in ReTraceQA; synthetic-data-heavy training gives a contrasting profile |
| Reserve | Gemma-3-4B-it | 4B | Swap in only if a generator fails the format check |

Selection criteria (from v1, unchanged): open weights, instruction-tuned, not math-specialised, roughly matched size (3–4B), runnable on a free GPU, and able to follow a numbered-step format.

Models to exclude from the main comparison:
- **Reasoning/"thinking" models** (for example R1-distills, or Qwen3 in thinking mode). Their very long traces make manual annotation impractical, and they are a different kind of system.
- **Math-specialised generators.** They would mix up model specialisation with task domain.

## 5. Trace generation protocol

- **Prompt:** one zero-shot template per task, using each model's own chat template, asking for:
  ```
  Step 1: ...
  Step 2: ...
  ...
  Final answer: <number | option letter>
  ```
  CommonsenseQA prompts list the options as `A. ... E.`. Both templates are versioned in the repo.
- **Decoding:** greedy (temperature 0), max 512 new tokens, fixed library versions, fixed seed.
- **Step segmentation:** split on `Step k:` markers, falling back to line breaks. **The same segmentation is used for human annotation, the judge and the PRM**, so step indices line up.
- **Record per trace (JSONL):** `trace_id`, `task`, `dataset`, `item_id`, `question`, `options`, `gold`, `model_id`, `model_revision`, `prompt_version`, `decoding`, `raw_output`, `steps[]`, `pred`, `answer_correct`, `format_ok`, `timestamp`.
- **Format failures** (no parsable final answer, or no steps) are counted and reported per model, kept out of the annotation sample, and not treated as reasoning failures.
- **Dry run:** 10 questions per dataset per model. Every model must reach a format-ok rate of at least 90% before the full run. If one doesn't, fix the prompt once; if it still fails, use the reserve model.

## 6. Sampling design (balanced sample)

### 6.1 Screening pool
- Draw a seeded random sample of **300 questions per dataset**.
- Run all three models on them: 1,800 traces, about 1–2 GPU-hours per model on a free T4.
- Score the answers automatically. **Accuracy and format rates in the report come from this pool**, so they reflect natural rates.

### 6.2 Stratify by failure pattern
For each question, let *k* = the number of models (0–3) that answered it wrong. Choose **75 shared questions per dataset** (all three models answer the same questions, which allows paired comparisons in RQ2):

| Stratum | Meaning | Questions per dataset | Wrong-answer traces |
|---|---|---:|---:|
| k = 0 | All models correct | 20 | 0 |
| k = 1 | One model wrong | 20 | 20 |
| k = 2 | Two models wrong | 20 | 40 |
| k = 3 | All models wrong | 15 | 45 |
| **Total** | | **75** | **105 of 225 (≈47%)** |

Rules:
- Within k = 1 and k = 2, balance *which* model failed (for k = 1, about 7 questions where each model is the only one wrong). This stops one model from dominating the failure set.
- If a stratum is too small, especially k = 3 on CSQA, take the shortfall from the nearest stratum and record the change.
- Correct-answer traces are kept on purpose. They are where process errors (correct answer, flawed reasoning) are found, which is a key RQ1 finding.

Result: **450 traces**, with about 70 wrong-answer and 80 correct-answer traces per model, split evenly across tasks.

### 6.3 Partitions
Each partition is drawn **proportionally from every stratum**:

| Partition | Questions per dataset | Traces (×2 datasets ×3 models) | Purpose |
|---|---:|---:|---|
| Discovery | 10 | 60 | Open coding |
| Pilot | 10 | 60 | Test the codebook, then freeze it |
| Main | 55 | 330 | Confirmatory annotation |
| **Total** | **75** | **450** | |

### 6.4 Reporting under stratified sampling
- Report failure-mode distributions **conditioned on outcome** (wrong-answer vs correct-answer traces). These are not biased by the sampling.
- For any population-level estimate (for example, the share of all correct answers that have flawed reasoning), **reweight each stratum** by its share of the screening pool, and say so.

## 7. Annotation

### 7.1 Principles
1. Judge the observable trace, not the model's hidden reasoning.
2. Trace validity is separate from answer correctness.
3. Mark the **earliest** step that contains an error, following ProcessBench. A step that only restates the question or a premise is not an error. An unsupported but true claim is flagged by a codebook rule, decided during the pilot.
4. Later errors caused by the first one are marked as propagated, not as new root failures.
5. Categories come from the data. ReTraceQA's three types are hypotheses to test.

### 7.2 Schema
| Field | Values |
|---|---|
| `trace_id`, `task`, `dataset`, `item_id`, `model_id`, `stratum_k`, `partition` | Identifiers and design variables |
| `answer_correct` | true / false (automatic) |
| `trace_valid` | true / false |
| `first_error_step` | integer, or -1 for no error |
| `primary_failure_parent` | taxonomy parent label |
| `primary_failure_child` | optional subtype |
| `propagated_error` | true / false |
| `secondary_failure` | optional independent second failure |
| `confidence` | 1–3 |
| `notes` | rationale for hard cases |

### 7.3 Taxonomy development
- **Discovery:** free-text descriptions of each failure → cluster into candidate categories → merge superficial splits and split categories that mix different mechanisms.
- Write an **inclusion rule, exclusion rule and examples** for each category.
- **Pilot:** apply the codebook, log every hard decision, revise, then **freeze it as v1.0** and record the freeze in git.
- Keep **4–6 parent categories** that are task-neutral, with task-specific children. Sketch only:
  - *Problem misreading* (grounding)
  - *Unsupported or false premise* (content; includes hallucinated facts or numbers)
  - *Invalid inference / transformation* (children: arithmetic or algebraic slip, causal leap, ...)
  - *Constraint or information omission*
  - *Answer–reasoning inconsistency*
- Rare categories are merged at the parent level for the quantitative analysis.

### 7.4 Workflow and reliability
- One researcher annotates in a spreadsheet or CSV, with the trace shown step by step and the model hidden where practical, to reduce bias in RQ2.
- **Self-consistency:** re-annotate a random ~10% of main traces at least 2 weeks later, and report Cohen's κ for validity and parent label, and agreement on the first-error step.
- **Supervisor:** reviews the codebook, all confidence-1 cases, and a sample of traces. *Optional:* double-labels 30 traces, which gives a cheap inter-annotator κ. **[CONFIRM]**
- **Time estimate:** about 4–6 min per trace, so 450 traces ≈ 30–45 hours of annotation.

## 8. Analysis

### RQ1
1. **Descriptive:** valid-trace rate, correct-answer-with-flawed-reasoning rate, and parent and child category counts by task, conditioned on outcome.
2. **Comparative:** categories in both tasks, mostly in one task, or only in one. Test the task × parent contingency table with χ² or Fisher's exact test, with bootstrap 95% CIs (resampling questions).
3. **Interpretive:** representative examples showing one mechanism appearing differently in each task, for example a lost constraint in math vs a lost fact in CSQA.

### RQ2
- Each model's failure profile is its distribution over parent categories, per task.
- **Profile similarity:** Jensen–Shannon distance between models, with bootstrap CIs.
- **Model × task interaction:** whether a model's profile on math differs from its profile on CSQA.
- **Paired view:** on shared k = 1 and k = 2 questions, check whether models fail the same question *for the same reason*.

### RQ3
| Evaluator | Tasks | Outputs compared to human labels |
|---|---|---|
| LLM judge | Math + CSQA | Validity, first-error step, parent category |
| Math PRM | Math only | Validity, first-error step |

- **Validity and localisation:** ProcessBench-style F1 (harmonic mean of accuracy on erroneous and on error-free traces), plus exact match of the first-error step on erroneous traces.
- **Category:** Cohen's κ, macro-F1 and a confusion matrix at the parent level.
- **PRM decision rule:** the first step whose score falls below 0.5 is the first error. The threshold is fixed beforehand or tuned on ProcessBench GSM8K, **never on our data**.
- **Bias check:** compare evaluator agreement separately for each generator. The PRM is Qwen-based and one generator is Qwen.

## 9. Automated evaluation set-up (free tools)

**LLM judge:** one free-tier API model from a family **not** among the generators (not Qwen, Llama or Phi), so the judge isn't rating its own family. As of Oct 2026, candidates are:
- **Google Gemini API free tier** (Flash models). Limits are listed in AI Studio.
- **Groq free tier: `gpt-oss-120b`** (about 30 requests/min, 1,000/day, OpenAI-compatible API).
- **OpenRouter `:free` models** (50 requests/day without credit). Use only as a fallback.

The workload is small: about 450 judge calls, plus about 400 calibration calls. Either of the first two fits inside a few days of free quota.

Rules for using the judge:
- Temperature 0, JSON output, the frozen codebook in the prompt, and the gold answer given (reference-based, as in v1).
- Log the exact model ID and date, and store every raw response.
- **Run all judge calls within a short window.** Free-tier models get retired without notice; Groq retired its Llama 3.3 70B in Aug 2026.
- *Optional:* run a second free judge as a robustness check, if quota allows.

**PRM:**
- Run Qwen2.5-Math-PRM-7B on a free GPU notebook (Kaggle or Colab). In fp16 the 7B model needs about 15–16 GB, which is tight on a single T4.
- **Fallback:** a smaller PRM (for example Skywork's 1.5B PRM), reported as such.
- Avoid 4-bit quantisation if possible, because it changes the scores. If it is used, report it.

**Calibration step:** before running on our traces, run both evaluators on the **ProcessBench GSM8K subset** and check that the PRM roughly reproduces the published F1. If it doesn't, the pipeline has a bug.

## 10. Deliverables
1. Protocol (this document), with a frozen version tagged in git.
2. Reproducible generation pipeline, configs and prompts.
3. Screening pool and annotated corpus (JSONL and CSV).
4. Hierarchical taxonomy and codebook v1.0, with examples and a change log.
5. RQ1, RQ2 and RQ3 analyses as notebooks.
6. Final report.

## 11. Risks and mitigation
| Risk | Mitigation |
|---|---|
| Too few failures per cell | Outcome-stratified sampling (§6) |
| Too few correct-answer/flawed-reasoning cases in math (≈3.5% in ProcessBench) | Report as a finding with CIs; don't build categories on these few cases alone |
| Format non-compliance | Dry-run gate, reserve model, format failures reported separately |
| Taxonomy too fine | 4–6 parent categories; merge rare children at the parent level |
| Annotation overruns | Freeze the codebook by week 5; cut RQ3 depth before cutting RQ1 |
| Free API changes or retirement | Run the judge in one window; log model IDs; keep a second provider ready |
| PRM doesn't fit the free GPU | Smaller fallback PRM; Kaggle instead of Colab |
| Single annotator | Self-re-annotation κ, supervisor review, optional 30-trace double-label |

## 12. Timeline (9 weeks)
| Week | Activity | Output |
|---|---|---|
| 1 | Confirm open decisions; HF access to the models; prompt templates; dry run | Protocol v2 signed off; format check passed |
| 2 | Build the pipeline; generate the screening pool (1,800 traces); score answers | Screening pool and accuracy table |
| 3 | Stratified selection; discovery coding (60 traces) | Candidate categories |
| 4 | Draft taxonomy and codebook | Codebook v0 |
| 5 | Pilot (60 traces); supervisor review; **freeze** | Codebook v1.0 |
| 6–7 | Main annotation (330); self-re-annotation sample | Annotated corpus |
| 8 | RQ1 and RQ2 analysis; set up judge and PRM; ProcessBench calibration | Results |
| 9 | RQ3 runs and analysis; write report | Final report |

## 13. Open decisions **[CONFIRM]**
1. **Supervisor sign-off on stratified sampling.** It changes which claims are allowed: natural rates come from the screening pool, failure profiles from the stratified sample.
2. **Compute:** a local GPU, or free Kaggle/Colab only?
3. **Hugging Face account with gated access to Llama-3.2-3B-Instruct.** Request it now, because approval can take time.
4. **Free API account** (Gemini and/or Groq), and whether your institution has rules about sending data to external APIs. The datasets are public, so this is usually fine.
5. **Supervisor time:** review only, or also the 30-trace double-label?
6. **Annotation time budget:** about 30–45 hours. Is that realistic alongside other work?
7. **Comparability with ReTraceQA:** should the final parent categories also map onto Misinterpretation / Hallucination / Reasoning?
8. **Start date and hard deadline,** and the report format expected (lab report vs thesis chapter).

## References
1. Molfese, F. M., Moroni, L., Porcaro, C., Conia, S., & Navigli, R. (2026). *ReTraceQA: Evaluating Reasoning Traces of Small Language Models in Commonsense Question Answering.* ACL 2026. https://aclanthology.org/2026.acl-long.1798/ (preprint: arXiv:2510.09351)
2. Zheng, C., Zhang, Z., Zhang, B., Lin, R., Lu, K., Yu, B., Liu, D., Zhou, J., & Lin, J. (2025). *ProcessBench: Identifying Process Errors in Mathematical Reasoning.* ACL 2025. https://aclanthology.org/2025.acl-long.50/ (code: https://github.com/QwenLM/ProcessBench)
3. Zhang, Z., et al. (2025). *The Lessons of Developing Process Reward Models in Mathematical Reasoning.* arXiv:2501.07301.
4. Qwen Team (2025). *Qwen2.5-Math-PRM-7B* model card. https://huggingface.co/Qwen/Qwen2.5-Math-PRM-7B
5. Cobbe, K., et al. (2021). *Training Verifiers to Solve Math Word Problems* (GSM8K). arXiv:2110.14168.
6. Talmor, A., Herzig, J., Lourie, N., & Berant, J. (2019). *CommonsenseQA: A Question Answering Challenge Targeting Commonsense Knowledge.* NAACL 2019.
