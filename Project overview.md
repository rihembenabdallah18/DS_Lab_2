# Formal Project Plan: Developing a Unified Reasoning Failure Mode Taxonomy for Small Language Models in QA Reasoning

## Executive summary

This project will develop and empirically evaluate a unified taxonomy of reasoning failure modes for Small Language Models (SLMs) in question-answering reasoning, with a focus on mathematical and commonsense QA. The project treats observable reasoning traces as the object of study rather than assuming that final-answer correctness is sufficient evidence of sound reasoning.

The study is structured around three research questions, but they will not be pursued with equal weight. The primary contribution is RQ1, which builds the taxonomy and identifies which failure modes are shared across mathematical and commonsense reasoning and which are task-specific. RQ2 is the second stage and uses the taxonomy to compare whether different SLMs exhibit similar or different failure profiles across tasks. RQ3 is the final stage and evaluates whether automated systems can reproduce parts of the human annotation process, using one general LLM judge across both tasks and one math-specific Process Reward Model (PRM) for mathematical error detection and localization.

The core design uses one math dataset and one commonsense dataset, one unified human annotation framework designed from scratch, approximately three comparable instruction-tuned SLMs, and a researcher-led annotation process with qualitative supervisor review. ReTraceQA and ProcessBench will serve as methodological anchors, but their taxonomies will not be copied directly; instead, the project will construct its own categories informed by their strengths and limitations.

## Project objective

The objective of the project is to create a practical, interpretable, and empirically grounded taxonomy of reasoning failures that can be applied to SLM-generated QA traces across at least two different reasoning domains. The taxonomy must be detailed enough to diagnose meaningful failure patterns, but compact enough to remain usable in manual annotation and later automated evaluation.

The project does not aim to prove anything about the models’ hidden internal reasoning processes. Instead, it studies the explicit text produced as a reasoning trace and asks whether that trace is valid, where it first becomes invalid, what type of failure occurs, and how those failures vary by task and model.

A second objective is methodological. The project will examine whether process-aware evaluation tools can support scalable oversight of reasoning traces, while recognizing that automated judges are not automatically valid substitutes for human labeling and must be compared against a structured reference annotation.

## Research questions and project order

The project is organized around the following research questions:

- **RQ1:** What failure modes are shared across math and commonsense reasoning, and which are task-specific?
- **RQ2:** Do different SLMs fail in different ways, or do they share a common failure profile across tasks?
- **RQ3:** How well can automated models detect and classify the proposed failure modes compared with human annotation?

The operational order of the project is:

1. **RQ1 first**
2. **RQ2 second**
3. **RQ3 last**

This order is required by the dependency structure of the study. RQ1 must come first because it defines the taxonomy, the annotation codebook, the labeling rules, and the human reference dataset. RQ2 can only be answered after those labels exist, because comparing model failure profiles requires a stable category system applied consistently across all traces. RQ3 must come last because automated detection and classification cannot be evaluated until the target labels are frozen and the annotation framework is stable.

## Scope of the project

The project scope has been intentionally narrowed to remain feasible within a 3–4 month lab timeline while preserving scientific value. It focuses on two reasoning domains represented in QA format: mathematical reasoning and commonsense reasoning.

The minimum scope includes:

- One mathematical QA dataset.
- One commonsense QA dataset.
- Approximately three instruction-tuned SLMs.
- One researcher-annotated trace corpus.
- A unified taxonomy created from scratch.
- One general LLM judge for both tasks.
- One math-specific PRM for mathematical detection and localization only.

The project explicitly excludes several larger extensions from the primary scope:

- Training a new PRM from scratch.
- Training a supervised failure classifier from the new annotations.
- Covering many QA domains beyond math and commonsense.
- Evaluating a large panel of automatic judges.
- Running a full-scale multi-annotator reliability study.

These excluded items are better framed as future thesis extensions rather than core lab deliverables.

## Role of prior literature

### ReTraceQA

ReTraceQA is a central methodological reference because it evaluates SLM-generated reasoning traces in commonsense QA and distinguishes between valid traces, invalid traces, and process errors where the final answer is correct but the reasoning is flawed. It also provides a hierarchical annotation logic, first-error localization, and a structured trace-evaluation procedure that is directly relevant to this project.

However, ReTraceQA’s taxonomy is intentionally coarse and limited to commonsense QA. The present project will borrow the ideas of trace validity, earliest-error identification, and process-aware annotation, but it will not directly adopt ReTraceQA’s fixed three-class structure because that would be too restrictive for a unified taxonomy spanning both math and commonsense reasoning.

### ProcessBench

ProcessBench is the main methodological reference for the mathematical side of the project. It evaluates whether automated systems can identify the earliest incorrect step in a mathematical reasoning process and compares prompted critic models with process reward models.

Its main value for this project lies in two contributions: first, it provides a strong precedent for step-level process evaluation in math; second, it motivates the inclusion of a PRM as a specialized automated evaluator for mathematical reasoning. At the same time, ProcessBench is not a unified cross-task taxonomy project, so it must be used as inspiration for mathematical error analysis rather than as the full template for the study.

### Broader reasoning-evaluation literature

The broader process-evaluation literature supports the contrast between mathematical reasoning and commonsense reasoning and shows that observable reasoning traces can reveal failures hidden by final-answer accuracy alone. It also supports the use of step-level evaluators such as PRMs for mathematics and LLM critics or judges for broader reasoning-trace analysis.

This literature justifies the central hypothesis of the project: some failure mechanisms may generalize across reasoning domains even if they appear differently on the surface. For example, losing a relevant constraint in a word problem and losing a relevant fact in commonsense QA may be domain-specific realizations of a more general grounding or omission failure.

## Dataset selection

### Mathematical reasoning dataset

The recommended mathematical dataset is GSM8K because it is widely used for multi-step mathematical reasoning and verifier research, and it aligns naturally with process-supervision work. It is more suitable for this project than very advanced competition mathematics because it keeps manual annotation interpretable and manageable while still requiring nontrivial reasoning.

### Commonsense reasoning dataset

The recommended commonsense dataset is CommonsenseQA because it is a standard multiple-choice benchmark that requires commonsense knowledge and semantic reasoning rather than simple lexical matching. It is also well aligned with the type of commonsense trace evaluation used in ReTraceQA.

### Scope of dataset coverage

The project will start with one dataset per task and may expand only if time allows. This means that claims about “task-specific” failures must be worded carefully, because some observed differences may reflect the selected datasets rather than the full domains of mathematical and commonsense reasoning.

## Model selection strategy

The recommended design uses approximately three instruction-tuned SLMs from different families but of broadly comparable scale. Three models provide a practical middle ground: one model is insufficient for RQ2, two models make generalization difficult, and four or more models would substantially increase annotation volume.

Model selection should follow the following criteria:

- Open or accessible enough for reproducible generation.
- Instruction-tuned rather than base-only.
- Small enough to fit the available compute setup.
- General-purpose rather than math-specialized for the main task comparison.
- Able to produce explicit step-by-step reasoning traces in a stable format.

A math-specialized generator could be studied later as an extension, but it should not be part of the primary three-model comparison because it would confound reasoning domain with model specialization.

## Trace generation protocol

Each selected question will be posed to every selected SLM using a fixed prompt template and fixed decoding protocol. The goal is to keep task and model comparisons meaningful by controlling the generation setting as much as possible.

Each generated record should contain:

- Question text and answer options if applicable.
- Model prompt.
- Raw generated response.
- Extracted reasoning steps.
- Extracted final answer.
- Final-answer correctness.
- Metadata such as model name, model version, decoding settings, and timestamp.

The response format should explicitly request numbered reasoning steps followed by a clearly marked final answer. This improves consistency for human annotation and later automated evaluation, including step-level scoring by PRMs and critics.

## Annotation philosophy

The annotation process will focus on observable reasoning traces, not hidden internal cognition. A trace may therefore be coherent, flawed, incomplete, misleading, or inconsistent even when the final answer is correct. This distinction is essential because prior work has shown that final-answer accuracy can overestimate actual reasoning quality.

The core annotation philosophy combines four principles:

1. **Trace validity matters separately from answer correctness.**
2. **The earliest independent failure should be identified when possible.**
3. **Failure categories should be defined from the data, not copied mechanically from prior work.**
4. **Later downstream mistakes should be separated from the first causal failure whenever possible.**

This means a trace can be marked as a process error when the final answer is correct but the earlier steps are flawed. It also means that a later arithmetic mistake caused entirely by an earlier misunderstanding may be recorded as propagated rather than treated as the primary root failure.

## Taxonomy-development method

The taxonomy will be designed from scratch using an iterative codebook-development approach informed by prior reasoning-trace evaluation work. Prior literature will inform the researcher’s expectations, but the final categories must be grounded in the actual trace corpus.

The recommended procedure is:

1. Read an initial discovery subset from both tasks without fixing labels in advance.
2. Write provisional descriptions of recurring failure mechanisms in plain language.
3. Group similar descriptions into candidate categories.
4. Merge categories that differ only superficially.
5. Split categories that conflate meaningfully distinct error mechanisms.
6. Define each category using explicit inclusion and exclusion rules.
7. Pilot the codebook on a separate subset.
8. Revise category definitions and decision rules.
9. Freeze the taxonomy before the main annotation stage.

The taxonomy should be hierarchical. A small set of shared high-level parent categories should capture task-neutral failure mechanisms, while optional child categories may capture domain-specific realizations. For example, a parent category such as unsupported inference or invalid transformation could appear in both tasks, while child categories distinguish arithmetic manipulation from commonsense causal leaps.

## Recommended annotation schema

Each trace should be annotated with a compact but expressive schema.

| Field | Purpose |
|---|---|
| `trace_id` | Unique reference for analysis |
| `task` | Math or commonsense |
| `dataset` | Dataset source |
| `item_id` | Original question ID |
| `model_id` | Model source for RQ2 |
| `answer_correct` | Outcome correctness |
| `trace_valid` | Overall process validity |
| `first_error_step` | Earliest erroneous step or none |
| `primary_failure_parent` | High-level taxonomy label |
| `primary_failure_child` | Optional fine-grained subtype |
| `propagated_error` | Whether later mistakes flow from earlier ones |
| `secondary_failure` | Optional additional independent failure |
| `confidence` | Annotation confidence |
| `notes` | Short rationale for difficult cases |

This schema is sufficient to support all three research questions. It captures outcome-versus-process distinctions for RQ1, model identity for RQ2, and reference labels for automatic evaluation in RQ3.

## Annotation workflow

The annotation workflow should proceed in three phases.

### Phase 1: discovery

A small subset of traces from both tasks will be read and coded openly without a frozen taxonomy. The purpose is to discover candidate failure categories, recurrent ambiguities, and potential parent–child structure.

### Phase 2: pilot

A second subset will be annotated with the draft codebook. This phase tests whether the taxonomy is usable, whether boundaries between categories are clear, and whether the earliest-error rule can be applied consistently.

### Phase 3: main annotation

Once the taxonomy is frozen, the remaining corpus will be annotated under the final codebook. All changes during this phase should be logged carefully; category definitions should not be changed informally once confirmatory annotation begins.

The supervisor’s role will be qualitative rather than fully independent second annotation. This means the supervisor should review the codebook, a sample of annotated traces, and the most ambiguous or low-confidence cases. This gives methodological support without expanding the project into a large formal reliability study.

## Sample size and partitioning

A balanced sample is important for both feasibility and interpretability. A suitable initial design is around 75 questions per dataset, answered by three models, giving approximately 450 traces in total.

A practical partition is:

| Partition | Questions per dataset | Approximate traces with 3 models | Purpose |
|---|---:|---:|---|
| Discovery subset | 10 | 60 | Open coding and category discovery |
| Pilot subset | 10 | 60 | Codebook testing and revision |
| Main analysis subset | 55 | 330 | Confirmatory annotation and analysis |
| Total | 75 | 450 | Full corpus |

This structure supports iterative development without contaminating the final confirmatory analysis. If time permits, the discovery and pilot subsets can be re-annotated under the frozen taxonomy and included in a secondary full-corpus analysis.

## RQ1 methodology

RQ1 is the primary contribution of the project. Its purpose is to determine which failure modes are shared across mathematical and commonsense reasoning and which are task-specific within the selected QA settings.

The RQ1 analysis should proceed in three layers:

1. **Descriptive layer:** frequency of valid traces, flawed traces, correct-answer/flawed-trace cases, and failure-category counts by task.
2. **Comparative layer:** identify which categories appear in both tasks, which are strongly concentrated in one task, and which seem meaningful only in one domain.
3. **Interpretive layer:** examine whether apparently different surface errors reflect the same underlying mechanism at a higher level of abstraction.

The key output of RQ1 is not merely a list of categories. It is a structured map showing which failures are likely task-general and which are genuinely task-linked. That map becomes the conceptual basis for the rest of the project.

## RQ2 methodology

RQ2 asks whether different SLMs fail in different ways or share a common failure profile across tasks. Once the taxonomy and annotations from RQ1 exist, each model can be represented by the distribution of failure categories across the selected tasks.

The main RQ2 analyses should include:

- Category frequency by model and task.
- Relative ranking of the most common failure categories per model.
- Similarity of model failure profiles at the parent-category level.
- Identification of model–task interactions, where a model behaves differently on math than on commonsense.

This question is secondary because it depends entirely on the successful completion of RQ1. Its value is diagnostic: it shows whether the taxonomy reveals stable model-specific patterns or whether failures are largely shared across small models regardless of family.

## RQ3 methodology

RQ3 evaluates how well automated systems can reproduce the proposed failure labels relative to the human annotation framework. This stage should remain intentionally limited so that it strengthens the project rather than overwhelming it.

### General LLM judge

One strong general LLM judge will be applied to both tasks. It will receive the question, the model-generated trace, the correct answer, and the frozen taxonomy definitions, and it will be asked to produce structured outputs for:

- Trace validity.
- First erroneous step if any.
- Failure-category label.

This evaluator is suitable for both mathematical and commonsense traces because it is not domain-restricted.

### Math-specific PRM

For the mathematical dataset, one specialized PRM will also be used. A practical candidate is Qwen2.5-Math-PRM-7B, which is designed to score the quality of intermediate mathematical reasoning steps.

The PRM should be used only for tasks it naturally supports:

- Detecting whether a mathematical trace is flawed.
- Identifying the first likely erroneous step.

It should not be expected to perform the full taxonomy classification unless the model is explicitly extended or wrapped for that purpose. Therefore, the human-versus-automation comparison for math will be asymmetric: the PRM supports detection and localization, while the general LLM judge supports detection, localization, and category classification.

### Why no new trained classifier

Training a new classifier or PRM is outside the primary project scope because this study is focused on taxonomy creation and empirical failure analysis rather than model training. Using existing evaluators is therefore the most realistic design choice for a 3–4 month project.

## Metrics and analysis strategy

The analysis should mix descriptive statistics with targeted qualitative examples. The project is not only counting failures; it is also trying to understand how failure categories behave across tasks and models.

Suggested outputs include:

- Final-answer accuracy by model and task.
- Valid-trace rate by model and task.
- Rate of process errors with correct final answers.
- Frequency of each parent and child failure category by task and by model.
- Distribution of first-error positions within traces.
- Agreement between automatic evaluators and human labels for trace validity, first-error localization, and category assignment.

Because the sample size is moderate, the most realistic inferential analysis is based on contingency tables, confidence intervals, and careful qualitative interpretation rather than overly complex modeling. Statistical testing can be included selectively, but the main emphasis should remain on interpretable distributions and representative annotated cases.

## Expected deliverables

The project should produce the following deliverables:

1. A formal research protocol.
2. A reproducible generation pipeline for SLM reasoning traces.
3. A hierarchical taxonomy of reasoning failure modes.
4. A written annotation codebook with definitions and examples.
5. A manually annotated trace corpus covering two QA tasks.
6. An RQ1 analysis of shared versus task-specific failures.
7. An RQ2 analysis of cross-model failure profiles.
8. An RQ3 analysis comparing human labels with an LLM judge and a math PRM.
9. A final written report suitable for supervisor review and future thesis continuation.

These deliverables are well aligned with the longer-term thesis direction because they create reusable data, methodology, and conceptual structure rather than a one-off benchmark result.

## Risks and mitigation

Several risks should be anticipated early.

| Risk | Why it matters | Mitigation |
|---|---|---|
| Taxonomy becomes too detailed | Categories become hard to apply consistently | Keep a small parent layer and only a few useful child categories |
| Annotation takes too long | The project may not reach RQ3 | Limit the corpus size and freeze the taxonomy early |
| Models produce inconsistent formats | Step parsing and annotation become harder | Use a strict response template with numbered steps |
| Rare categories appear too infrequently | Quantitative comparison becomes unstable | Merge sparse categories at the parent level for main analysis |
| PRM does not align with human categories | RQ3 results become hard to interpret | Evaluate PRM mainly on detection and localization, not full classification |
| Supervisor review is limited | Reliability evidence remains weak | Keep detailed annotation notes and perform spot-check review on ambiguous cases |

These mitigation choices preserve the main contribution even if some secondary analyses become narrower than planned.

## Timeline

A 9-week execution timeline fits the project well.

| Week | Main activity | Output |
|---|---|---|
| 1 | Finalize scope, datasets, model list, prompt template | Protocol draft |
| 2 | Implement trace-generation and parsing pipeline | Working generation setup |
| 3 | Generate dry-run traces and discovery subset | Early examples and candidate categories |
| 4 | Develop draft taxonomy and codebook | Taxonomy v0 and codebook draft |
| 5 | Pilot annotation and supervisor review | Revised taxonomy and frozen codebook |
| 6 | Generate or finalize the full corpus | Complete dataset for main annotation |
| 7 | Main annotation and audit | Annotated corpus |
| 8 | RQ1 and RQ2 analysis | Comparative results |
| 9 | RQ3 automated evaluation and report writing | Final project report |

If annotation takes longer than expected, the best fallback is to preserve RQ1 and RQ2 at full quality and reduce the depth of RQ3 rather than weakening the taxonomy stage. This keeps the central scientific contribution intact.

## Final project framing

The final framing of the project is as follows. The study will construct a unified taxonomy of reasoning failures in SLM-generated QA traces across mathematics and commonsense reasoning, apply that taxonomy to a balanced corpus generated by multiple SLMs, and use the resulting annotations to compare cross-task and cross-model failure profiles. It will then perform a limited automated-evaluation study using a general LLM judge across both tasks and a specialized PRM for mathematics.

This design is ambitious enough to be research-worthy but controlled enough to be feasible in a short academic project. It also creates a strong bridge to future thesis work, where the taxonomy, corpus, and evaluation framework can later be expanded to more datasets, more domains, stronger annotation validation, and richer automated classifiers.

## References

1. Francesco Maria Molfese, Luca Moroni, Ciro Porcaro, Simone Conia, and Roberto Navigli. 2026. *ReTraceQA: Evaluating Reasoning Traces of Small Language Models in Commonsense Question Answering*. In *Proceedings of the 64th Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers)*. Association for Computational Linguistics. Available at: [ACL Anthology](https://aclanthology.org/2026.acl-long.1798/).

2. Chujie Zheng, Zhenru Zhang, Beichen Zhang, Runji Lin, Keming Lu, Bowen Yu, Dayiheng Liu, Jingren Zhou, and Junyang Lin. 2025. *ProcessBench: Identifying Process Errors in Mathematical Reasoning*. In *Proceedings of the 63rd Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers)*. Association for Computational Linguistics. Available at: [ACL Anthology](https://aclanthology.org/2025.acl-long.50/).

3. Qwen Team. 2024. *Qwen2.5-Math-PRM-7B*. Model card. Available at: [Hugging Face](https://huggingface.co/Qwen/Qwen2.5-Math-PRM-7B).

4. Qwen Team. 2025. *Towards Effective Process Supervision in Mathematical Reasoning*. Available at: [Qwen Blog](https://qwenlm.github.io/blog/qwen2.5-math-prm/).

5. QwenLM. 2024. *ProcessBench official repository*. Available at: [GitHub](https://github.com/QwenLM/ProcessBench).

6. QwenLM. 2024. *Qwen2.5-MATH repository*. Available at: [GitHub](https://github.com/QwenLM/Qwen2.5-MATH).

7. OpenReview PDF version of *ReTraceQA*. Available at: [OpenReview PDF](https://openreview.net/pdf?id=kqArTgW53f).

8. *The Lessons of Developing Process Reward Models in Mathematical Reasoning*. 2025. Available at: [arXiv PDF](https://arxiv.org/pdf/2501.07301.pdf).
