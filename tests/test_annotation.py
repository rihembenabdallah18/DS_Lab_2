import pandas as pd

from slm_traces.annotation import build_sheet, export_xlsx, load_taxonomy, validate_row, validate_sheet
from slm_traces.generate import make_trace_id

TAX = load_taxonomy()


def row(**kw):
    base = {
        "trace_id": "t1", "answer_correct": "FALSE", "trace_valid": "FALSE", "first_error_step": "2",
        "primary_failure_parent": "INFERENCE", "primary_failure_child": "INFERENCE.operation",
        "propagated_error": "TRUE", "secondary_failure": "none", "confidence": "3", "notes": "",
    }
    return {**base, **kw}


def test_valid_example_passes():
    assert validate_row(row(), n_steps=3, taxonomy=TAX) == []


def test_valid_trace_rules():
    ok = row(answer_correct="TRUE", trace_valid="TRUE", first_error_step="-1",
             primary_failure_parent="", primary_failure_child="", propagated_error="")
    assert validate_row(ok, 3, TAX) == []
    assert validate_row({**ok, "first_error_step": "2"}, 3, TAX)
    assert validate_row({**ok, "answer_correct": "FALSE"}, 3, TAX)


def test_step_range_allows_final_answer_line():
    assert validate_row(row(first_error_step="4"), 3, TAX) == []
    assert validate_row(row(first_error_step="5"), 3, TAX)
    assert validate_row(row(first_error_step="0"), 3, TAX)


def test_child_must_belong_to_parent():
    assert validate_row(row(primary_failure_child="PREMISE.fact"), 3, TAX)
    assert validate_row(row(primary_failure_parent="NOPE"), 3, TAX)


def test_low_confidence_needs_note():
    assert validate_row(row(confidence="1"), 3, TAX)
    assert validate_row(row(confidence="1", notes="unsure between MISREAD and OMISSION"), 3, TAX) == []


def test_sheet_is_blind_and_round_trips(tmp_path):
    traces, selection = [], []
    for q in range(2):
        selection.append({"dataset": "gsm8k", "item_id": f"q{q}", "k": 1, "partition": "pilot"})
        for m in ["m1", "m2", "m3"]:
            traces.append({
                "trace_id": make_trace_id("gsm8k", f"q{q}", m), "dataset": "gsm8k", "task": "math",
                "item_id": f"q{q}", "model_id": m, "question": "Q?", "options": [], "gold": "8",
                "final_answer_text": "8", "answer_correct": True, "steps": ["a", "b"],
            })
    rows, key = build_sheet(traces, selection, "pilot", seed=0)
    assert len(rows) == 6 and len(key) == 6
    assert all("model_id" not in r for r in rows)
    assert rows[0]["steps"] == "[1] a\n[2] b"

    path = tmp_path / "sheet.xlsx"
    export_xlsx(rows, path, TAX)
    back = pd.read_excel(path, sheet_name="traces", dtype=str).to_dict("records")
    assert [r["trace_id"] for r in back] == [r["trace_id"] for r in rows]
    problems = validate_sheet(back, TAX)
    assert problems == ["6 trace(s) not annotated yet"]
