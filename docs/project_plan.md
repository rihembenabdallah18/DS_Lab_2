# Project Plan (v2): A Unified Reasoning Failure Taxonomy for Small Language Models in QA

> **Status:** revised draft for supervisor review. Items marked **[CONFIRM]** are open decisions (collected in the last section).

## What changed from v1

| Area | v1 | v2 | Why |
|---|---|---|---|
| Sampling | 75 random questions per dataset (450 traces) | Run all models on a larger **screening pool** (300 questions per dataset), then pick 60 **shared** questions per dataset, **stratified by how many models got each one wrong**: **360 traces** to annotate | 3–4B models answer most GSM8K/CSQA questions correctly, so a random sample would give too few failures. 360 keeps one person's annotation work at about 32 hours (§7.5) |
| Annotation workflow | Discovery → pilot → main | Draft taxonomy from an informal read → **pilot of 60 traces** → supervisor review (optionally blind-labels 24) → **freeze** → annotate the remaining 300 | Matches the researcher-then-supervisor workflow |
| Models | "About three SLMs" | Qwen2.5-3B-Instruct, Llama-3.2-3B-Instruct, Phi-4-mini-instruct | These are the same families ReTraceQA used, at matched size, which keeps the commonsense results comparable |
| Splits | Unspecified | GSM8K **test** (1,319); CommonsenseQA **validation** (1,221) | CommonsenseQA test answers are not public |
| Compute and automated evaluation | Unspecified | All GPU work on **Kaggle** (free 2×T4). Free-tier API judge from a family **not** among the generators | The project has no budget for paid APIs or GPUs |
| Calibration | None | Sanity-check the PRM and judge set-up on ProcessBench's GSM8K subset (human labels) before using them on our data | Separates "our pipeline is broken" from "the evaluator disagrees with us" |
| Reliability | Supervisor qualitative review only | Plus an optional 24-trace blind supervisor label during the pilot, and a 30-trace self-re-annotation | Cheap evidence of label stability without a full multi-annotator study |
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

Selection criteria (from v1, unchanged): open weights, instruction-tuned, not math-specialised, roughly matched size (3–4B), runnable on a free Kaggle GPU, and able to follow a numbered-step format.

Models to exclude from the main comparison:
- **Reasoning/"thinking" models** (for example R1-distills, or Qwen3 in thinking mode). Their very long traces make manual annotation impractical, and they are a different kind of system.
- **Math-specialised generators.** They would mix up model specialisation with task domain.

## 5. Trace generation protocol

- **Prompt:** one zero-shot chain-of-thought template per task, identical for all three models and sent through each model's own chat template.

  Math (GSM8K):
  ```
  Solve the following math problem. Reason step by step.
  Write each step on its own line, numbered as "Step 1:", "Step 2:", and so on.
  After the last step, write the final answer on its own line in exactly this format:
  Final answer: <number>

  Problem: {question}
  ```
  Commonsense (CommonsenseQA): the same wording, with `Question: {question}` followed by the options `A. … E.`, and `Final answer: <letter>`.

- **Why this prompt** (relation to prior work):

  | Choice | Reason |
  |---|---|
  | Zero-shot (no worked examples) | Matches ReTraceQA's zero-shot chain-of-thought set-up, so the commonsense results stay comparable. Example solutions would make models copy their style and change their natural failures |
  | Numbered `Step k:` lines | Each step needs a clear index for "first wrong step", and the PRM needs separated steps. ProcessBench split free-form solutions into steps afterwards; asking for numbered steps directly is more reliable for manual annotation |
  | Fixed `Final answer:` line | Makes the automatic answer check reliable |
  | Same prompt for every model | Fair comparison for RQ2 |

  *Risk:* a forced format can slightly change how a model reasons, and small models may ignore it. The dry run checks this. If ReTraceQA's exact prompt wording (paper appendix) is available, align the wording with it.
- **Decoding:** greedy (temperature 0), max 512 new tokens, fixed library versions, fixed seed.
- **Step segmentation:** split on `Step k:` markers, falling back to line breaks. **The same segmentation is used for human annotation, the judge and the PRM**, so step indices line up.
- **Record per trace (JSONL):** `trace_id`, `task`, `dataset`, `item_id`, `question`, `options`, `gold`, `model_id`, `model_revision`, `prompt_version`, `decoding`, `raw_output`, `steps[]`, `pred`, `answer_correct`, `format_ok`, `timestamp`.
- **Format failures** (no parsable final answer, or no steps) are counted and reported per model, kept out of the annotation sample, and not treated as reasoning failures.
- **Dry run:** 10 questions per dataset per model. Every model must reach a format-ok rate of at least 90% before the full run. If one doesn't, fix the prompt once; if it still fails, use the reserve model.

## 6. Sampling design (balanced sample)

### 6.1 Screening pool
- Draw a seeded random sample of **300 questions per dataset**.
- Run all three models on them: 1,800 traces, about 1–2 GPU-hours per model on Kaggle.
- **These traces are not annotated**, only scored automatically.
- Score the answers automatically. **Accuracy and format rates in the report come from this pool**, so they reflect natural rates.

### 6.2 Stratify by failure pattern
For each question, let *k* = the number of models (0–3) that answered it wrong. Choose **60 shared questions per dataset** (all three models answer the same questions, which allows paired comparisons in RQ2):

| Stratum | Meaning | Questions per dataset | Wrong-answer traces |
|---|---|---:|---:|
| k = 0 | All models correct | 16 | 0 |
| k = 1 | One model wrong | 16 | 16 |
| k = 2 | Two models wrong | 16 | 32 |
| k = 3 | All models wrong | 12 | 36 |
| **Total** | | **60** | **84 of 180 (≈47%)** |

Rules:
- Within k = 1 and k = 2, balance *which* model failed (for k = 1, about 5 questions where each model is the only one wrong). This stops one model from dominating the failure set.
- If a stratum is too small, especially k = 3 on CSQA, take the shortfall from the nearest stratum and record the change.
- Correct-answer traces are kept on purpose. They are where process errors (correct answer, flawed reasoning) are found, which is a key RQ1 finding.

Result: **360 traces** (180 per task). Each model has about 28 wrong-answer and 32 correct-answer traces per task, which is enough to compare parent-level categories.

### 6.3 Partitions
Each partition is drawn **proportionally from every stratum**:

| Partition | Questions per dataset | Traces (×2 datasets ×3 models) | Purpose |
|---|---:|---:|---|
| Pilot | 10 (3 / 3 / 2 / 2 across k = 0–3) | 60 | First annotation with the proposed taxonomy; supervisor review |
| Main | 50 | 300 | Annotated with the frozen taxonomy |
| **Total** | **60** | **360** | |

Taxonomy discovery uses **extra screening-pool traces that are not in the 360** (see §7.3), so no annotation-sample traces are used up.

After the freeze, the pilot traces are re-labelled under the final taxonomy. This is quick because they've already been read, and it brings them into the final corpus, giving 360 for RQ1–RQ3. A sensitivity check reports the main results on the 300 main traces alone.

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

### 7.3 Workflow: from proposed taxonomy to full corpus

| Stage | Who | Traces | What happens | Output |
|---|---|---:|---|---|
| **A. Informal read** | Researcher | ~30 (not in the 360) | Read about 15 wrong-answer screening-pool traces per task and fill in the short note format below. Then group similar descriptions into categories and compare them with ReTraceQA's and ProcessBench's error types | Proposed taxonomy v0: a name, a one-line definition and one example per category |
| **B. Pilot annotation** | Researcher | 60 | Fully annotate the pilot partition with v0. Log every case the codebook doesn't settle | Pilot labels and a list of hard cases |
| **C. Supervisor review** | Supervisor | 60 reviewed; *optionally* 24 blind | Reads the codebook, all confidence-1 cases and the hard-case list. *Optional:* independently labels 24 pilot traces (2 per model × task × correct/wrong) without seeing yours, about 2 hours of supervisor time | Comments, plus agreement figures if the blind labels are done |
| **D. Revise and freeze** | Both | n/a | Discuss disagreements, then merge, split or redefine categories. Freeze as **v1.0** and tag it in git. After this, definitions change only through a logged decision | Final taxonomy and codebook v1.0 |
| **E. Main annotation** | Researcher | 300 + 60 re-label | Annotate the main partition with v1.0, about 150 per week. Re-label the 60 pilot traces under v1.0 | Final corpus of 360 |
| **F. Self-check** | Researcher | 30 | Re-annotate 30 random main traces at least 2 weeks after first labelling them, without looking at the old labels | Self-agreement figures (Cohen's κ) |

**Stage A note format** (deliberately simple; the full label set in §7.2 starts with the pilot):

| Field | What to write |
|---|---|
| `trace_id` | The trace being read |
| `reasoning_valid` | yes / no |
| `first_error_step` | Number of the first wrong step |
| `description` | One sentence in your own words, e.g. "added instead of multiplied", "invented a number not in the problem", "claimed penguins can fly" |
| `confidence` | 1 = unsure, 2 = fairly sure, 3 = clear |
| `note` | Optional: an independent later error, or anything odd |

Only the **first** error is described, because later mistakes usually just follow from it; this matches ProcessBench and ReTraceQA, and it is what the RQ3 evaluators are tested on. An independent later error gets a short note only.

Wrong-answer traces are used for stage A because each one is guaranteed to contain a failure. Correct-answer traces, where hidden errors may be found, are included from the pilot onwards.

To avoid steering the descriptions, write them **before** looking at the category sketch below; use the sketch only afterwards, as a comparison.

**Parent categories:** keep **4–6**, task-neutral, with task-specific children. The v0 sketch below is a comparison point after stage A, not something to adopt:
- *Problem misreading* (grounding)
- *Unsupported or false premise* (content; includes hallucinated facts or numbers)
- *Invalid inference / transformation* (children: arithmetic or algebraic slip, causal leap, ...)
- *Constraint or information omission*
- *Answer–reasoning inconsistency*

Rare children are merged into their parent category for the quantitative analysis.

While waiting for the supervisor in stage C, the researcher can prepare the RQ3 calibration on ProcessBench (§9), which doesn't depend on the taxonomy.

### 7.4 Annotating one trace

Each trace is one spreadsheet row, with its steps numbered. Drop-down lists hold the category labels, and the model name is hidden. The procedure:

1. Read the question and gold answer (and the options for CSQA). The `answer_correct` field is already filled in automatically.
2. Go through the steps in order. For each step ask: *is this true, and does it follow from the question and earlier steps?*
3. The first step that fails is `first_error_step`. If none fails, enter `-1`, set `trace_valid = true` and stop. **A correct, valid trace takes 1–3 minutes.**
4. Give the first error a parent category (and a child if one fits).
5. Mark `propagated_error = true` if later steps go wrong *because of* that first error.
6. If a later, *unrelated* error appears, record it in `secondary_failure`.
7. Set `confidence` (1 = unsure, 3 = clear) and write a short note if confidence is 1.

**Worked example (GSM8K, made up):**
> Q: *A shop sells pens at $3 each. Tom buys 4 pens and pays with a $20 bill. How much change does he get?* Gold: 8
> Step 1: Each pen costs $3. · Step 2: Tom buys 4 pens, so 3 + 4 = 7. · Step 3: 20 − 7 = 13. · Final answer: 13

→ `answer_correct=false`, `trace_valid=false`, `first_error_step=2`, parent = *Invalid inference / transformation*, child = *wrong operation*, `propagated_error=true` (step 3 is right given step 2), `secondary_failure=none`, `confidence=3`.

### 7.5 Workload
| Stage | Traces | Minutes per trace | Hours |
|---|---:|---:|---:|
| A. Informal read | ~30 | ~3 (notes only) | ~1.5 |
| B. Pilot (slower: codebook is new) | 60 | ~7 | ~7 |
| E. Main: correct-answer traces | ~160 | ~2.5 | ~7 |
| E. Main: wrong-answer traces | ~140 | ~5.5 | ~13 |
| E. Pilot re-label | 60 | ~2 | ~2 |
| F. Self-check | 30 | ~4 | ~2 |
| **Total (researcher)** | | | **≈ 32 h over ~5 weeks** |

The supervisor needs about 2–3 hours for review, plus about 2 hours if they do the optional blind labels.

If time runs short, cut the main partition to 40 questions per dataset (240 main traces, 300 in total) rather than shortening the pilot. Do this before sampling, not halfway through.

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

## 9. Compute, model access and automated evaluation (free tools)

**Compute: Kaggle notebooks.**
- Free GPU quota of about 30 hours/week (check the current figure on your Kaggle quota page). Choose the **GPU T4 ×2** accelerator.
- **Phone verification is required** before GPU and internet can be turned on in notebook settings.
- T4s don't support bf16, so load models in **fp16**.
- Save outputs (JSONL) to `/kaggle/working` and download them, or publish them as a private Kaggle dataset, after each run. Sessions end after a time limit.
- Estimated GPU use: about 1 hour for the dry run, about 3–6 hours for the screening pool, and about 1–2 hours for the PRM. That fits inside one week's quota.

**Model access (Hugging Face).**
- Qwen2.5-3B-Instruct and Phi-4-mini-instruct download without any approval.
- **Llama-3.2-3B-Instruct is "gated":** you must accept Meta's licence on its Hugging Face page and wait for approval before it downloads. Steps:
  1. Create a free account at huggingface.co.
  2. Open `meta-llama/Llama-3.2-3B-Instruct` and fill in the licence form. Use your real name and university.
  3. Wait for the "access granted" email.
  4. Create a **Read** access token under Settings → Access Tokens.
  5. In Kaggle, open Add-ons → Secrets, add it as `HF_TOKEN`, and log in from the notebook with `huggingface_hub.login()`.
- **Fallback if access is refused or delayed for more than a week:** Kaggle's own Models hub also hosts Llama 3.2 behind a separate licence acceptance. Otherwise use the reserve model (Gemma-3-4B-it, which also needs a one-click licence acceptance).
- **Never commit the token to git.**


**LLM judge:** one free-tier API model from a family **not** among the generators (not Qwen, Llama or Phi), so the judge isn't rating its own family. As of Oct 2026, candidates are:
- **Google Gemini API free tier** (Flash models). Limits are listed in AI Studio.
- **Groq free tier: `gpt-oss-120b`** (about 30 requests/min, 1,000/day, OpenAI-compatible API).
- **OpenRouter `:free` models** (50 requests/day without credit). Use only as a fallback.

The workload is small: about 360 judge calls, plus about 400 calibration calls. Either of the first two fits inside a few days of free quota.

Rules for using the judge:
- Temperature 0, JSON output, the frozen codebook in the prompt, and the gold answer given (reference-based, as in v1).
- Log the exact model ID and date, and store every raw response.
- **Run all judge calls within a short window.** Free-tier models get retired without notice; Groq retired its Llama 3.3 70B in Aug 2026.
- *Optional:* run a second free judge as a robustness check, if quota allows.

**PRM:**
- Run Qwen2.5-Math-PRM-7B on Kaggle. In fp16 the 7B model needs about 15–16 GB, which is too tight for one T4, so **split it across both T4s** (`device_map="auto"`). Only the 180 math traces and about 400 ProcessBench items are scored.
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
| Llama access delayed | Request it in week 1; use Kaggle Models or the reserve model as a fallback |
| Supervisor review takes longer than a week | Do the RQ3 ProcessBench calibration while waiting; main annotation starts only after the freeze |
| Free API changes or retirement | Run the judge in one window; log model IDs; keep a second provider ready |
| PRM doesn't fit the free GPU | Split across Kaggle's 2×T4; otherwise a smaller fallback PRM |
| Single annotator | Supervisor review, optional 24-trace blind supervisor label, 30-trace self-check |

## 12. Timeline (9 weeks)
| Week | Activity | Output |
|---|---|---|
| 1 | Supervisor sign-off on v2; Kaggle phone verification; HF account and **Llama access request**; API key; prompt templates; dry run | Protocol agreed; format check passed |
| 2 | Pipeline; screening pool (1,800 traces); answer scoring; stratified selection of the 360 | Accuracy table; annotation sheet |
| 3 | Stage A informal read (~30 traces); taxonomy v0 and codebook draft | Codebook v0 |
| 4 | Stage B pilot annotation (60); send to supervisor | Pilot labels and hard-case list |
| 5 | Stage C supervisor review (optionally 24 blind labels); stage D revise and **freeze**. *Meanwhile:* ProcessBench calibration for RQ3 | Codebook v1.0 |
| 6–7 | Stage E main annotation (300) and pilot re-label (60) | Corpus of 360 |
| 8 | Stage F self-check (30); RQ1 and RQ2 analysis | Results |
| 9 | RQ3: judge on 360, PRM on 180 math traces; write report | Final report |

## 13. Open decisions **[CONFIRM]**
1. **Supervisor sign-off on stratified sampling** and on the 360-trace size. These change which claims are allowed: natural rates come from the screening pool, failure profiles from the stratified sample.
2. ~~Compute~~: **decided, Kaggle.**
3. **Llama access:** request it in week 1 (steps in §9).
4. **Free API account** (Gemini and/or Groq), and whether your institution has rules about sending data to external APIs. The datasets are public, so this is usually fine.
5. **Supervisor involvement:** review only, or also the 24-trace blind labels? About 2 extra hours of their time, and it gives a real agreement figure.
6. **Annotation time:** about 32 hours over weeks 3–8. Is that realistic alongside other work? If not, use the 300-trace fallback (§7.5).
7. **Comparability with ReTraceQA:** should the final parent categories also map onto Misinterpretation / Hallucination / Reasoning?
8. **Start date and hard deadline,** and the report format expected (lab report vs thesis chapter).

## References
1. Molfese, F. M., Moroni, L., Porcaro, C., Conia, S., & Navigli, R. (2026). *ReTraceQA: Evaluating Reasoning Traces of Small Language Models in Commonsense Question Answering.* ACL 2026. https://aclanthology.org/2026.acl-long.1798/ (preprint: arXiv:2510.09351)
2. Zheng, C., Zhang, Z., Zhang, B., Lin, R., Lu, K., Yu, B., Liu, D., Zhou, J., & Lin, J. (2025). *ProcessBench: Identifying Process Errors in Mathematical Reasoning.* ACL 2025. https://aclanthology.org/2025.acl-long.50/ (code: https://github.com/QwenLM/ProcessBench)
3. Zhang, Z., et al. (2025). *The Lessons of Developing Process Reward Models in Mathematical Reasoning.* arXiv:2501.07301.
4. Qwen Team (2025). *Qwen2.5-Math-PRM-7B* model card. https://huggingface.co/Qwen/Qwen2.5-Math-PRM-7B
5. Cobbe, K., et al. (2021). *Training Verifiers to Solve Math Word Problems* (GSM8K). arXiv:2110.14168.
6. Talmor, A., Herzig, J., Lourie, N., & Berant, J. (2019). *CommonsenseQA: A Question Answering Challenge Targeting Commonsense Knowledge.* NAACL 2019.
