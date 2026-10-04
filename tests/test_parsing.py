from slm_traces.parsing import extract_letter, extract_number, parse_response
from slm_traces.scoring import is_correct, score_trace

CSQA_OPTIONS = [{"label": l, "text": t} for l, t in zip("ABCDE", ["bank", "library", "park", "store", "house"])]


def test_numbered_steps_and_final_answer():
    raw = "Let's solve it.\nStep 1: Pens cost $3 each.\nStep 2: 4 pens cost 3 * 4 = 12.\nStep 3: 20 - 12 = 8.\nFinal answer: 8"
    p = parse_response(raw, "math")
    assert p["steps"] == ["Pens cost $3 each.", "4 pens cost 3 * 4 = 12.", "20 - 12 = 8."]
    assert p["pred"] == "8"
    assert p["format_ok"]


def test_markdown_bold_markers():
    raw = "**Step 1:** Read it.\n**Step 2:** 2 + 2 = 4\n\n**Final answer:** 4"
    p = parse_response(raw, "math")
    assert p["steps"] == ["Read it.", "2 + 2 = 4"]
    assert p["pred"] == "4"


def test_multiline_step_kept_together():
    raw = "Step 1: First line\ncontinued here.\nStep 2: Done.\nFinal answer: 5"
    assert parse_response(raw, "math")["steps"] == ["First line\ncontinued here.", "Done."]


def test_missing_final_answer_is_format_failure():
    p = parse_response("Step 1: Something.\nSo the answer is 5.", "math")
    assert p["pred"] is None
    assert not p["format_ok"]


def test_uses_last_final_answer_line():
    raw = "Step 1: x.\nFinal answer: 3\nStep 2: Actually y.\nFinal answer: 4"
    p = parse_response(raw, "math")
    assert p["pred"] == "4"
    assert p["steps"] == ["x.\nFinal answer: 3", "Actually y."]


def test_no_step_markers_falls_back_to_lines():
    p = parse_response("First we add.\nThen we subtract.\nFinal answer: 2", "math")
    assert p["steps"] == ["First we add.", "Then we subtract."]


def test_extract_number_variants():
    assert extract_number("$1,234.") == "1234"
    assert extract_number("18.50 dollars") == "18.50"
    assert extract_number("-3") == "-3"
    assert extract_number("no number") is None


def test_extract_letter_variants():
    assert extract_letter("B", CSQA_OPTIONS) == "B"
    assert extract_letter("(C) park", CSQA_OPTIONS) == "C"
    assert extract_letter("D. store", CSQA_OPTIONS) == "D"
    assert extract_letter("library", CSQA_OPTIONS) == "B"   # option text, no letter
    assert extract_letter("Bank", CSQA_OPTIONS) == "A"      # matches option text, not the B in "Bank"
    assert extract_letter("Bunk beds", CSQA_OPTIONS) is None


def test_is_correct():
    assert is_correct("18.00", "18", "math")
    assert not is_correct("17", "18", "math")
    assert is_correct("b", "B", "commonsense")
    assert not is_correct(None, "B", "commonsense")


def test_score_trace_marks_format_failures_wrong():
    t = {"raw_output": "The answer is 8", "task": "math", "gold": "8", "options": []}
    s = score_trace(t)
    assert not s["format_ok"] and not s["answer_correct"]
