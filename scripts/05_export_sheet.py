"""Step 5: export a blind annotation sheet for one partition.

    python scripts/05_export_sheet.py --partition pilot
    python scripts/05_export_sheet.py --partition main

Writes annotation/sheets/<partition>_sheet.xlsx (no model names) and
data/annotation_set/<partition>_key.csv (trace_id -> model, item, k). Don't open the key while annotating.
Refuses to overwrite an existing sheet so labels are never lost.
"""

import argparse

import pandas as pd

from slm_traces import ROOT
from slm_traces.annotation import KEY_COLUMNS, build_sheet, export_xlsx, load_taxonomy
from slm_traces.io import load_config, read_jsonl


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--partition", choices=["pilot", "main"], required=True)
    args = ap.parse_args()

    sheet_path = ROOT / "annotation" / "sheets" / f"{args.partition}_sheet.xlsx"
    if sheet_path.exists():
        raise SystemExit(f"{sheet_path.relative_to(ROOT)} already exists; move it away first")

    traces = read_jsonl(ROOT / "data" / "traces" / "screening_scored.jsonl")
    selection = pd.read_csv(ROOT / "data" / "annotation_set" / "selection.csv", dtype={"item_id": str})
    rows, key = build_sheet(traces, selection.to_dict("records"), args.partition, load_config("sampling")["seed"])

    taxonomy = load_taxonomy()
    export_xlsx(rows, sheet_path, taxonomy)
    pd.DataFrame(key, columns=KEY_COLUMNS).to_csv(
        ROOT / "data" / "annotation_set" / f"{args.partition}_key.csv", index=False
    )
    print(f"{len(rows)} traces -> {sheet_path.relative_to(ROOT)} (taxonomy {taxonomy['version']})")


if __name__ == "__main__":
    main()
