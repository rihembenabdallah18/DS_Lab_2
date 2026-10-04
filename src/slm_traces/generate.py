"""Generate reasoning traces with Hugging Face transformers (run on Kaggle GPUs).

Output is one JSONL record per (item, model), written batch by batch so a Kaggle session
that times out can resume: items whose trace_id is already in the output file are skipped.
Parsing and scoring happen later (scoring.py), so a parser fix never requires regeneration.
"""

import hashlib
from datetime import datetime, timezone

from .io import read_jsonl, write_jsonl
from .prompts import build_prompt, load_template


def make_trace_id(dataset: str, item_id: str, model_key: str) -> str:
    """Opaque, stable ID: it must not reveal the model to the annotator."""
    return "t" + hashlib.sha1(f"{dataset}|{item_id}|{model_key}".encode()).hexdigest()[:12]


def load_model(hf_id: str, dtype: str = "float16"):
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    tokenizer = AutoTokenizer.from_pretrained(hf_id)
    tokenizer.padding_side = "left"   # decoder-only models need left padding for batching
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    model = AutoModelForCausalLM.from_pretrained(hf_id, torch_dtype=getattr(torch, dtype), device_map="auto")
    model.eval()
    return tokenizer, model


def generate_traces(items, model_cfg: dict, gen_cfg: dict, dtype: str, out_path, tokenizer=None, model=None) -> int:
    """Generate traces for `items` with one model, appending to `out_path`. Returns the number generated."""
    import torch
    import transformers

    done = {r["trace_id"] for r in read_jsonl(out_path)}
    todo = [it for it in items if make_trace_id(it["dataset"], it["item_id"], model_cfg["key"]) not in done]
    if not todo:
        return 0
    if tokenizer is None or model is None:
        tokenizer, model = load_model(model_cfg["hf_id"], dtype)

    torch.manual_seed(gen_cfg["seed"])
    templates = {name: load_template(path) for name, path in gen_cfg["prompts"].items()}
    template_kwargs = model_cfg.get("chat_template_kwargs", {})
    decoding = gen_cfg["decoding"]
    meta = {
        "model_id": model_cfg["key"],
        "hf_id": model_cfg["hf_id"],
        "model_revision": getattr(model.config, "_commit_hash", None),
        "prompt_version": gen_cfg["prompt_version"],
        "decoding": decoding,
        "transformers_version": transformers.__version__,
        "torch_version": torch.__version__,
    }

    bs = gen_cfg["batch_size"]
    for start in range(0, len(todo), bs):
        batch = todo[start: start + bs]
        prompts = [build_prompt(templates[it["dataset"]], it) for it in batch]
        chats = [
            tokenizer.apply_chat_template(
                [{"role": "user", "content": p}], tokenize=False, add_generation_prompt=True, **template_kwargs
            )
            for p in prompts
        ]
        enc = tokenizer(chats, return_tensors="pt", padding=True, add_special_tokens=False).to(model.device)
        with torch.no_grad():
            out = model.generate(
                **enc,
                do_sample=decoding["do_sample"],
                max_new_tokens=decoding["max_new_tokens"],
                pad_token_id=tokenizer.pad_token_id,
            )
        new_tokens = out[:, enc["input_ids"].shape[1]:]
        texts = tokenizer.batch_decode(new_tokens, skip_special_tokens=True)
        now = datetime.now(timezone.utc).isoformat(timespec="seconds")
        records = []
        for it, prompt, text, toks in zip(batch, prompts, texts, new_tokens):
            n_tokens = int((toks != tokenizer.pad_token_id).sum())
            records.append({
                "trace_id": make_trace_id(it["dataset"], it["item_id"], model_cfg["key"]),
                **it,
                "prompt": prompt,
                "raw_output": text.strip(),
                "n_output_tokens": n_tokens,
                "truncated": n_tokens >= decoding["max_new_tokens"],
                **meta,
                "timestamp": now,
            })
        write_jsonl(out_path, records, append=True)
    return len(todo)
