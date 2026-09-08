"""Platform formatters (§14). Real transformations driven by rules.py config."""
from __future__ import annotations

from .rules import get_rules


def format_linkedin(topic: str, angle: str, body_core: str, tone: str, cta: str = "") -> tuple[str, str, str]:
    rules = get_rules("LinkedIn")
    cta = cta or rules["default_cta"]
    hook = f"{topic}: what changed and what to do about it."
    core = body_core.strip()
    takes = "\n".join(f"{i+1}) {t}" for i, t in enumerate(rules["takeaways"]))
    body = f"{hook}\n\n{core}\n\n{takes}\n\n{cta}" if core else f"{hook}\n\n{takes}\n\n{cta}"
    return hook, body, cta


def format_x(topic: str, angle: str, body_core: str, tone: str) -> tuple[str, str, str]:
    hook = f"{topic} in one line: {angle[:110]}" if angle else f"{topic}: the short version."
    core = body_core[:180].strip()
    tweets = [hook]
    if core:
        tweets.append(core)
    tweets.append("Takeaway: apply this to one small task this week.")
    body = "\n\n".join(f"{i+1}/ {t}" for i, t in enumerate(tweets))
    return hook, body, get_rules("X")["default_cta"]


def format_blog(topic: str, angle: str, body_core: str, tone: str) -> tuple[str, str, str]:
    rules = get_rules("Blog")
    title = f"{topic}: a practical guide ({(tone or 'technical').split('+')[0].strip()})"
    body = (
        f"# {title}\n\n## Why now\n{body_core}\n\n"
        f"## How it works\n1. Background\n2. Example\n3. Pitfalls\n\n"
        f"## What to do next\nTry one small experiment and measure the result.\n"
    )
    return title, body, rules["default_cta"]


def format_newsletter(topic: str, angle: str, body_core: str, tone: str) -> tuple[str, str, str]:
    rules = get_rules("Newsletter")
    subject = f"{topic}: what changed this week"
    body = (
        f"Subject: {subject}\n\nHi —\n\n{body_core.strip()}\n\n"
        f"One thing to try: apply it to a single small task this week.\n\n"
        f"{rules['default_cta']}"
    )
    return subject, body, rules["default_cta"]
