"""Load GSM8K and CommonsenseQA into one item format and draw the seeded screening pool.

Item format:
    {"dataset", "task", "item_id", "question", "options", "gold"}
`options` is a list of {"label", "text"} for CSQA and empty for GSM8K.
`gold` is the numeric answer as a string (GSM8K) or the option letter (CSQA).
"""

import random


def _gsm8k_gold(answer: str) -> str:
    # GSM8K solutions end with "#### <number>".
    return answer.split("####")[-1].strip().replace(",", "")


def normalize(dataset: str, task: str, rows) -> list[dict]:
    items = []
    for i, row in enumerate(rows):
        if dataset == "gsm8k":
            items.append({
                "dataset": dataset,
                "task": task,
                "item_id": f"gsm8k-test-{i:04d}",   # GSM8K has no IDs; use the row index
                "question": row["question"],
                "options": [],
                "gold": _gsm8k_gold(row["answer"]),
            })
        elif dataset == "csqa":
            items.append({
                "dataset": dataset,
                "task": task,
                "item_id": row["id"],
                "question": row["question"],
                "options": [
                    {"label": label, "text": text}
                    for label, text in zip(row["choices"]["label"], row["choices"]["text"])
                ],
                "gold": row["answerKey"],
            })
        else:
            raise ValueError(f"unknown dataset: {dataset}")
    return items


def load_dataset_items(dataset: str, cfg: dict) -> list[dict]:
    """Download one dataset split from Hugging Face and normalize it."""
    from datasets import load_dataset  # imported here so tests don't need `datasets`

    d = cfg["datasets"][dataset]
    rows = load_dataset(d["hf_id"], d["hf_config"], split=d["split"])
    return normalize(dataset, d["task"], rows)


def sample_pool(items: list[dict], n: int, seed: int) -> list[dict]:
    """Seeded random sample, returned in original dataset order."""
    rng = random.Random(seed)
    idx = sorted(rng.sample(range(len(items)), n))
    return [items[i] for i in idx]
