"""Step 3: parse and score all traces of a stage, and write the accuracy / format table.

    python scripts/03_score.py --stage dryrun
    python scripts/03_score.py --stage screening

Writes data/traces/<stage>_scored.jsonl and results/tables/<stage>_summary.csv.
For the dry run, also reports whether each model passes the format gate.
"""

import argparse

from slm_traces import ROOT
from slm_traces.io import load_config, read_jsonl, write_jsonl
from slm_traces.scoring import score_trace, summarize


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", choices=["dryrun", "screening"], default="screening")
    args = ap.parse_args()

    files = sorted((ROOT / "data" / "traces" / args.stage).glob("*.jsonl"))
    if not files:
        raise SystemExit(f"no trace files in data/traces/{args.stage}/")
    scored = [score_trace(t) for f in files for t in read_jsonl(f)]
    write_jsonl(ROOT / "data" / "traces" / f"{args.stage}_scored.jsonl", scored)

    table = summarize(scored)
    out = ROOT / "results" / "tables" / f"{args.stage}_summary.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    table.to_csv(out, index=False)
    print(table.to_string(index=False))

    truncated = sum(t.get("truncated", False) for t in scored)
    if truncated:
        print(f"\nwarning: {truncated} trace(s) hit max_new_tokens")
    if args.stage == "dryrun":
        gate = load_config("generation")["min_format_ok_rate"]
        failing = table[table["format_ok"] < gate]
        print("\nformat gate:", "PASSED" if failing.empty else f"FAILED for\n{failing.to_string(index=False)}")


if __name__ == "__main__":
    main()
