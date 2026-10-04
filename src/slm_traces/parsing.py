"""Split a raw model response into numbered steps and a final answer.

Steps are numbered from 1, matching the "Step k:" labels the model was asked to write;
these are the indices used for `first_error_step` (with -1 meaning no error).
Text before "Step 1:" is not a step. Parsing is deliberately strict: a response without a
"Final answer:" line is a format failure, not a guess.
"""

import re

STEP_RE = re.compile(r"^[ \t>*#_-]*step\s*(\d+)\s*[:.)\-]+\**[ \t]*", re.IGNORECASE | re.MULTILINE)
FINAL_RE = re.compile(r"^[ \t>*#_-]*final\s+answer\s*\**\s*[:：]\s*\**\s*(.*)$", re.IGNORECASE | re.MULTILINE)
NUMBER_RE = re.compile(r"-?\d[\d,]*(?:\.\d+)?|-?\.\d+")
LETTER_RE = re.compile(r"(?<![A-Za-z])\(?([A-E])\)?(?![A-Za-z])")


def split_final(raw: str) -> tuple[str, str | None]:
    """Return (body before the last 'Final answer:' line, answer text or None)."""
    matches = list(FINAL_RE.finditer(raw))
    if not matches:
        return raw, None
    last = matches[-1]
    return raw[: last.start()], last.group(1).strip()


def split_steps(body: str) -> list[str]:
    """Split on 'Step k:' markers; fall back to non-empty lines if there are none."""
    markers = list(STEP_RE.finditer(body))
    if not markers:
        return [ln.strip() for ln in body.splitlines() if ln.strip()]
    steps = []
    for m, nxt in zip(markers, markers[1:] + [None]):
        text = body[m.end(): nxt.start() if nxt else len(body)].strip()
        steps.append(text)
    return steps


def extract_number(text: str) -> str | None:
    """Last number in the answer text, without thousands separators or a trailing '.'."""
    nums = NUMBER_RE.findall(text.replace("$", ""))
    if not nums:
        return None
    return nums[-1].replace(",", "").rstrip(".")


def extract_letter(text: str, options: list[dict]) -> str | None:
    """Option letter from the answer text; falls back to an exact option-text match."""
    m = LETTER_RE.search(text.strip())
    if m:
        return m.group(1)
    norm = text.strip().strip(".").lower()
    for o in options:
        if o["text"].strip().lower() == norm:
            return o["label"]
    return None


def parse_response(raw: str, task: str, options: list[dict] | None = None) -> dict:
    body, answer_text = split_final(raw)
    steps = split_steps(body)
    if answer_text is None:
        pred = None
    elif task == "math":
        pred = extract_number(answer_text)
    else:
        pred = extract_letter(answer_text, options or [])
    return {
        "steps": steps,
        "final_answer_text": answer_text,
        "pred": pred,
        "format_ok": pred is not None and len(steps) > 0,
    }
