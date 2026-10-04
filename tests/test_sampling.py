import itertools
import random

from slm_traces.sampling import assign_partitions, question_table, select_stratified

MODELS = ["m1", "m2", "m3"]


def make_traces(n_questions=300, seed=0):
    rng = random.Random(seed)
    traces = []
    for q in range(n_questions):
        for m in MODELS:
            traces.append({
                "dataset": "gsm8k", "item_id": f"q{q:03d}", "model_id": m,
                "format_ok": True, "answer_correct": rng.random() < 0.5,
            })
    return traces


def test_question_table_computes_k_and_skips_format_failures():
    traces = make_traces(5)
    traces[0]["format_ok"] = False                  # q000 becomes ineligible
    rows = question_table(traces, MODELS)
    assert len(rows) == 4
    for r in rows:
        assert r["k"] == len(r["failed_models"])


def test_selection_meets_allocation_and_balances_models():
    rows = question_table(make_traces(), MODELS)
    alloc = {0: 16, 1: 16, 2: 16, 3: 12}
    chosen, notes = select_stratified(rows, alloc, seed=1)
    counts = {k: sum(r["k"] == k for r in chosen) for k in alloc}
    assert notes == []
    assert counts == alloc
    assert len(chosen) == sum(alloc.values())
    assert len({r["item_id"] for r in chosen}) == len(chosen)    # no duplicates
    # k=1: each model should be the sole failure in 5 or 6 of the 16 questions
    sole = [r["failed_models"][0] for r in chosen if r["k"] == 1]
    assert max(sole.count(m) for m in MODELS) - min(sole.count(m) for m in MODELS) <= 1


def test_shortfall_is_filled_from_nearest_stratum():
    rows = [r for r in question_table(make_traces(), MODELS) if r["k"] != 3][:200]
    rows += [r for r in question_table(make_traces(seed=5), MODELS) if r["k"] == 3][:4]
    for i, r in enumerate(rows):
        r["item_id"] = f"x{i:03d}"
    chosen, notes = select_stratified(rows, {0: 16, 1: 16, 2: 16, 3: 12}, seed=1)
    assert len(chosen) == 60
    assert any("filled 8 from k=2" in n for n in notes)


def test_selection_is_reproducible():
    rows = question_table(make_traces(), MODELS)
    a, _ = select_stratified(rows, {0: 16, 1: 16, 2: 16, 3: 12}, seed=7)
    b, _ = select_stratified(rows, {0: 16, 1: 16, 2: 16, 3: 12}, seed=7)
    assert [r["item_id"] for r in a] == [r["item_id"] for r in b]


def test_partitions():
    rows = question_table(make_traces(), MODELS)
    chosen, _ = select_stratified(rows, {0: 16, 1: 16, 2: 16, 3: 12}, seed=1)
    parts = assign_partitions(chosen, {0: 3, 1: 3, 2: 2, 3: 2}, seed=1)
    pilot = [r for r in parts if r["partition"] == "pilot"]
    assert len(pilot) == 10 and len(parts) == 60
    assert {k: sum(r["k"] == k for r in pilot) for k in range(4)} == {0: 3, 1: 3, 2: 2, 3: 2}
    assert not any(a == b for a, b in itertools.combinations([r["item_id"] for r in parts], 2))
