"""Step 4: choose the 60 shared questions per dataset, stratified by k, and split pilot / main.

    python scripts/04_select_annotation_set.py

Writes data/annotation_set/selection.csv and prints the stratum counts and any shortfalls.
"""

import pandas as pd

from slm_traces import ROOT
from slm_traces.io import load_config, read_jsonl
from slm_traces.sampling import assign_partitions, question_table, select_stratified


def main():
    cfg = load_config("sampling")
    models = [m["key"] for m in load_config("models")["generators"]]
    traces = read_jsonl(ROOT / "data" / "traces" / "screening_scored.jsonl")
    if not traces:
        raise SystemExit("run scripts/03_score.py --stage screening first")

    selection = []
    for dataset in cfg["datasets"]:
        rows = question_table([t for t in traces if t["dataset"] == dataset], models)
        chosen, notes = select_stratified(rows, cfg["allocation"], cfg["seed"])
        selection += assign_partitions(chosen, cfg["pilot_allocation"], cfg["seed"])
        print(f"{dataset}: {len(rows)} eligible questions, {len(chosen)} selected")
        for n in notes:
            print("  note:", n)

    df = pd.DataFrame(selection)
    df["failed_models"] = df["failed_models"].map(lambda t: ";".join(t))
    out = ROOT / "data" / "annotation_set" / "selection.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out, index=False)
    print()
    print(df.groupby(["dataset", "partition", "k"]).size().unstack(fill_value=0))


if __name__ == "__main__":
    main()
