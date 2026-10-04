"""Answer correctness and per-model summary tables."""

from .parsing import parse_response


def is_correct(pred: str | None, gold: str, task: str) -> bool:
    if pred is None:
        return False
    if task == "math":
        try:
            return abs(float(pred) - float(gold)) < 1e-6
        except ValueError:
            return False
    return pred.strip().upper() == gold.strip().upper()


def score_trace(trace: dict) -> dict:
    """Add parsed steps, prediction, format flag and correctness to a raw trace record."""
    parsed = parse_response(trace["raw_output"], trace["task"], trace.get("options"))
    return {
        **trace,
        **parsed,
        "answer_correct": parsed["format_ok"] and is_correct(parsed["pred"], trace["gold"], trace["task"]),
    }


def summarize(traces: list[dict]):
    """Accuracy and format-ok rate per dataset and model."""
    import pandas as pd

    df = pd.DataFrame(traces)
    df["n_steps"] = df["steps"].map(len)
    out = (
        df.groupby(["dataset", "model_id"])
        .agg(
            n=("trace_id", "size"),
            format_ok=("format_ok", "mean"),
            accuracy=("answer_correct", "mean"),
            mean_steps=("n_steps", "mean"),
        )
        .reset_index()
    )
    return out.round(3)
