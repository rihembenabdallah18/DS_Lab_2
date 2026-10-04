"""Outcome-stratified selection of the annotation set (plan §6.2–6.3).

Every selected question is answered by all generators (shared-question design).
k = number of generators whose final answer is wrong. Questions where any generator
had a format failure are not eligible.
"""

import random
from collections import defaultdict


def question_table(traces: list[dict], models: list[str]) -> list[dict]:
    """One row per (dataset, item_id) with k and the tuple of models that failed."""
    by_q = defaultdict(dict)
    for t in traces:
        by_q[(t["dataset"], t["item_id"])][t["model_id"]] = t
    rows = []
    for (dataset, item_id), per_model in sorted(by_q.items()):
        if set(per_model) != set(models):
            continue
        if not all(per_model[m]["format_ok"] for m in models):
            continue
        failed = tuple(m for m in models if not per_model[m]["answer_correct"])
        rows.append({"dataset": dataset, "item_id": item_id, "k": len(failed), "failed_models": failed})
    return rows


def _round_robin(candidates: list[dict], n: int, rng: random.Random) -> list[dict]:
    """Pick n candidates, cycling over failure patterns so no single model dominates."""
    groups = defaultdict(list)
    for c in candidates:
        groups[c["failed_models"]].append(c)
    keys = sorted(groups)
    for key in keys:
        rng.shuffle(groups[key])
    rng.shuffle(keys)
    picked = []
    while len(picked) < n and any(groups[k] for k in keys):
        for key in keys:
            if groups[key] and len(picked) < n:
                picked.append(groups[key].pop())
    return picked


def select_stratified(rows: list[dict], allocation: dict, seed: int) -> tuple[list[dict], list[str]]:
    """Select questions per k for one dataset. Shortfalls are filled from the nearest stratum.

    Returns (selected rows, notes describing any shortfall).
    """
    rng = random.Random(seed)
    pool = defaultdict(list)
    for r in rows:
        pool[r["k"]].append(r)
    alloc = {int(k): v for k, v in allocation.items()}
    selected, notes = [], []

    for k in sorted(alloc):
        got = _round_robin(pool[k], alloc[k], rng)
        for r in got:
            pool[k].remove(r)
        selected += got
        short = alloc[k] - len(got)
        if short:
            notes.append(f"k={k}: wanted {alloc[k]}, found {len(got)}")
        # Fill from the nearest strata, preferring the one with more failures on ties.
        for other in sorted((s for s in alloc if s != k), key=lambda s: (abs(s - k), -s)):
            if not short:
                break
            extra = _round_robin(pool[other], short, rng)
            for r in extra:
                pool[other].remove(r)
            selected += extra
            short -= len(extra)
            if extra:
                notes.append(f"k={k}: filled {len(extra)} from k={other}")
        if short:
            notes.append(f"k={k}: still short by {short}; selection is smaller than planned")
    return selected, notes


def assign_partitions(selected: list[dict], pilot_allocation: dict, seed: int) -> list[dict]:
    """Mark each selected question as 'pilot' or 'main', drawing the pilot from every stratum by actual k."""
    rng = random.Random(seed)
    by_k = defaultdict(list)
    for r in selected:
        by_k[r["k"]].append(r)
    out = []
    for k in sorted(by_k):
        group = sorted(by_k[k], key=lambda r: r["item_id"])
        rng.shuffle(group)
        n_pilot = min(int(pilot_allocation.get(k, pilot_allocation.get(str(k), 0))), len(group))
        out += [{**r, "partition": "pilot" if i < n_pilot else "main"} for i, r in enumerate(group)]
    return out
