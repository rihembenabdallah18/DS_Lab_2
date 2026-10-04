"""Step 2: generate traces with one model on one dataset (run on a Kaggle GPU).

    python scripts/02_generate.py --model qwen2.5-3b --dataset gsm8k --stage dryrun
    python scripts/02_generate.py --model qwen2.5-3b --dataset all --stage screening

Writes data/traces/<stage>/<dataset>__<model>.jsonl. Re-running resumes where it stopped.
"""

import argparse

from slm_traces import ROOT
from slm_traces.generate import generate_traces, load_model
from slm_traces.io import load_config, read_jsonl


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True, help="model key from configs/models.yaml")
    ap.add_argument("--dataset", default="all", help="gsm8k, csqa or all")
    ap.add_argument("--stage", choices=["dryrun", "screening"], default="screening")
    args = ap.parse_args()

    models_cfg = load_config("models")
    gen_cfg = load_config("generation")
    all_models = models_cfg["generators"] + models_cfg["reserve"]
    model_cfg = next((m for m in all_models if m["key"] == args.model), None)
    if model_cfg is None:
        raise SystemExit(f"unknown model key {args.model}; choose from {[m['key'] for m in all_models]}")

    datasets = list(gen_cfg["prompts"]) if args.dataset == "all" else [args.dataset]
    suffix = "dryrun" if args.stage == "dryrun" else "pool"
    tokenizer, model = load_model(model_cfg["hf_id"], models_cfg["dtype"])
    for dataset in datasets:
        items = read_jsonl(ROOT / "data" / "pool" / f"{dataset}_{suffix}.jsonl")
        if not items:
            raise SystemExit(f"no items for {dataset}; run scripts/01_build_pool.py first")
        out = ROOT / "data" / "traces" / args.stage / f"{dataset}__{args.model}.jsonl"
        n = generate_traces(items, model_cfg, gen_cfg, models_cfg["dtype"], out, tokenizer, model)
        print(f"{dataset} / {args.model}: generated {n} new traces -> {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
