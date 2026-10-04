# Annotation Codebook

**Version:** v0 (draft; hypotheses to be tested in stage A and the pilot) · **Machine-readable labels:** [`taxonomy.yaml`](taxonomy.yaml) · **Changes:** [`changelog.md`](changelog.md)

This codebook says how to label one reasoning trace. When a case isn't covered, label it as best you can, set confidence to 1, explain in `notes`, and add it to the hard-case list for the supervisor review. **Don't change a definition mid-sheet.** Definitions change only between stages, with an entry in the changelog.

---

## 1. Unit of annotation

One **trace** = one model's response to one question, split into numbered steps `[1] … [n]`, followed by the model's final answer.

You see:
- the question (and the options for CSQA)
- the gold answer
- the model's final answer
- whether it is correct (filled in automatically)

The model's name is hidden.

## 2. Procedure

1. Read the question and the gold answer.
2. Go through the steps in order. For each step ask: **is this step true, and does it follow from the question and the earlier steps?**
3. The first step that fails is `first_error_step`.
   - If no step fails and the final answer matches the steps, enter `-1` and set `trace_valid = TRUE`. **Stop here.**
   - If every step is fine but the `Final answer:` line contradicts them, enter `n + 1` (one past the last step).
4. Give that first error a `primary_failure_parent`, and a `primary_failure_child` if one fits.
5. `propagated_error`: `TRUE` if later steps go wrong *because of* the first error, `FALSE` otherwise.
6. `secondary_failure`: the category of a later, **independent** error, if there is one; otherwise `none`.
7. `confidence`: 3 = clear, 2 = some doubt, 1 = unsure. **Confidence 1 requires a note.**

Run `python scripts/06_validate_annotations.py <sheet>` after each session to catch inconsistent rows.

## 3. Decision rules

| # | Situation | Rule |
|---|---|---|
| R1 | A step only restates the question or a premise correctly | Not an error |
| R2 | A step is irrelevant but true and harmless | Not an error |
| R3 | A step makes a true claim the question doesn't support, and the reasoning depends on it | *To decide in the pilot.* Proposal: an error only if the claim is doubtful or the conclusion relies on it |
| R4 | Correct final answer but a flawed step | `trace_valid = FALSE` (a **process error**). Label it like any other error |
| R5 | Wrong final answer | The trace cannot be valid. Find the first failing step, or use `n + 1` |
| R6 | An error caused entirely by an earlier error | Not a new root failure: it is the propagation of the first one (`propagated_error = TRUE`) |
| R7 | Two errors in the same step | Label the one that came first logically; record the other as `secondary_failure` |
| R8 | Rounding or units, e.g. writing 7.5 as 8 when the problem needs 7.5 | `INFERENCE.arithmetic` if it changes the result; otherwise not an error |
| R9 | CSQA: the model picks an option that is plausible but not the best | `OMISSION.alternative` if the steps never weigh the better option; `INFERENCE.leap` if they weigh it and reason badly |
| R10 | The model hedges or picks two options | `INCONSISTENCY.answer` at step `n + 1` if the final answer doesn't follow; otherwise label the step where the hedging starts |

*Add new rules here as the pilot raises them (R11, R12, …), each with a changelog entry.*

## 4. Categories (v0)

Each category needs, by the freeze:
- a **definition**
- an **include** rule (what belongs here)
- an **exclude** rule (what looks similar but belongs elsewhere)
- at least one **example per task** where it applies

The `OTHER` category is for stage A and the pilot. It should be close to empty by the freeze.

### MISREAD: Problem misreading *(grounding)*
- **Definition:** the model misunderstands what the question gives or asks.
- **Include:** wrong quantity or relation copied from the problem; solving for a different target; misreading an option.
- **Exclude:** a correctly read fact that is then used badly (→ INFERENCE); a fact that is ignored rather than misread (→ OMISSION).
- **Children:** `MISREAD.quantity` (math), `MISREAD.target` (both), `MISREAD.options` (commonsense).
- **Examples:** *to add in stage A.*

### PREMISE: Unsupported or false premise *(content)*
- **Definition:** the model introduces a claim that is false or unverifiable and isn't in the question.
- **Include:** hallucinated world knowledge; numbers that appear from nowhere.
- **Exclude:** a misread number that *is* in the problem (→ MISREAD.quantity).
- **Children:** `PREMISE.fact` (both), `PREMISE.number` (math).
- **Examples:** *to add in stage A.*

### INFERENCE: Invalid inference or transformation *(reasoning)*
- **Definition:** correct inputs, wrong output: the step doesn't follow.
- **Include:** arithmetic slips; the wrong operation or equation; conclusions that don't follow from the premises.
- **Exclude:** a wrong input (→ MISREAD or PREMISE).
- **Children:** `INFERENCE.arithmetic` (math), `INFERENCE.operation` (math), `INFERENCE.leap` (both).
- **Examples:** *to add in stage A.*

### OMISSION: Constraint or information omission *(grounding)*
- **Definition:** the model drops something the question requires.
- **Include:** a skipped condition or sub-step; ignoring a better-fitting option.
- **Exclude:** misreading the dropped item (→ MISREAD).
- **Children:** `OMISSION.constraint` (both), `OMISSION.alternative` (commonsense).
- **Examples:** *to add in stage A.*

### INCONSISTENCY: Answer–reasoning inconsistency *(reasoning)*
- **Definition:** the trace contradicts itself.
- **Include:** a final answer that doesn't match the steps; a step that contradicts an earlier one.
- **Exclude:** a wrong step that later steps faithfully build on (→ the first error, with propagation).
- **Children:** `INCONSISTENCY.answer` (both), `INCONSISTENCY.steps` (both).
- **Examples:** *to add in stage A.*

### OTHER
- Anything that doesn't fit. **Describe it in `notes`.** Recurring OTHER notes become new categories at the next revision.

## 5. Worked example

> **Q (GSM8K, made up):** A shop sells pens at $3 each. Tom buys 4 pens and pays with a $20 bill. How much change does he get? **Gold:** 8
> [1] Each pen costs $3.
> [2] Tom buys 4 pens, so 3 + 4 = 7.
> [3] 20 − 7 = 13.
> Final answer: 13

| Field | Value | Why |
|---|---|---|
| `trace_valid` | FALSE | Step 2 is wrong |
| `first_error_step` | 2 | Step 1 is a correct restatement (R1) |
| `primary_failure_parent` / `child` | INFERENCE / INFERENCE.operation | The inputs were read correctly; the operation was wrong |
| `propagated_error` | TRUE | Step 3 is correct arithmetic on a wrong value |
| `secondary_failure` | none | |
| `confidence` | 3 | |

## 6. Field reference

| Field | Values |
|---|---|
| `trace_valid` | TRUE / FALSE |
| `first_error_step` | -1 (no error), 1…n (that step), n + 1 (only the final-answer line) |
| `primary_failure_parent` | A parent ID from `taxonomy.yaml`; blank if valid |
| `primary_failure_child` | A child ID of that parent, or blank |
| `propagated_error` | TRUE / FALSE; blank if valid |
| `secondary_failure` | `none` or any parent/child ID |
| `confidence` | 1 / 2 / 3 |
| `notes` | Free text; required when confidence is 1 |
