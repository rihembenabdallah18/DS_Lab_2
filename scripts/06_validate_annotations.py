"""Step 6: check an annotation sheet against the codebook rules. Run it after every session.

    python scripts/06_validate_annotations.py annotation/sheets/pilot_sheet.xlsx
"""

import argparse

import pandas as pd

from slm_traces.annotation import load_taxonomy, validate_sheet


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("sheet")
    args = ap.parse_args()

    rows = pd.read_excel(args.sheet, sheet_name="traces", dtype=str).to_dict("records")
    problems = validate_sheet(rows, load_taxonomy())
    if not problems:
        print(f"OK: {len(rows)} traces, all annotated and consistent")
    for p in problems:
        print("-", p)


if __name__ == "__main__":
    main()
