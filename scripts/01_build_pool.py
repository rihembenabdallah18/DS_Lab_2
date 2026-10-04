"""Step 1: download GSM8K and CommonsenseQA and draw the seeded screening pools.

    python scripts/01_build_pool.py

Writes data/pool/<dataset>_pool.jsonl (300 items each) and <dataset>_dryrun.jsonl
(the first 10 pool items, for the format check).
"""

from slm_traces import ROOT
from slm_traces.data import load_dataset_items, sample_pool
from slm_traces.io import load_config, write_jsonl


def main():
    cfg = load_config("sampling")
    for dataset in cfg["datasets"]:
        items = load_dataset_items(dataset, cfg)
        pool = sample_pool(items, cfg["pool_size"], cfg["seed"])
        write_jsonl(ROOT / "data" / "pool" / f"{dataset}_pool.jsonl", pool)
        write_jsonl(ROOT / "data" / "pool" / f"{dataset}_dryrun.jsonl", pool[: cfg["dry_run_size"]])
        print(f"{dataset}: {len(items)} items -> pool of {len(pool)}")


if __name__ == "__main__":
    main()
