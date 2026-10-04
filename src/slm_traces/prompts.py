"""Fill the versioned prompt templates in prompts/."""

from . import ROOT


def load_template(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def format_options(options: list[dict]) -> str:
    return "\n".join(f"{o['label']}. {o['text']}" for o in options)


def build_prompt(template: str, item: dict) -> str:
    return template.format(question=item["question"], options=format_options(item["options"])).strip()
