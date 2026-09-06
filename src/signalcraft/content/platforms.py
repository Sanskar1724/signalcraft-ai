"""Platform formatters. Real transformations, not truncation."""
from __future__ import annotations


def format_linkedin(topic: str, angle: str, body_core: str, tone: str, cta: str = "") -> tuple[str, str, str]:
    hook = f"{topic}: what changed and what to do about it."
    body = (
        f"{hook}\n\n{body_core.strip()}\n\n"
        f"Angle: {angle.strip()}\n\n"
        f"3 takeaways:\n1) Why it matters now\n2) One concrete example\n3) What to try this week\n\n"
        f"{cta or 'What is working for you?'}"
    )
    return hook, body, cta or "What is working for you?"


def format_x(topic: str, angle: str, body_core: str, tone: str) -> tuple[str, str, str]:
    hook = f"{topic} in one line: {angle[:110]}"
    tweets = [
        hook,
        f"Context: {body_core[:180].strip()}",
        f"Takeaway: apply this to one small task this week. Tone: {tone or 'sharp'}.",
    ]
    body = "\n\n".join(f"{i+1}/ {t}" for i, t in enumerate(tweets))
    return hook, body, ""


def format_blog(topic: str, angle: str, body_core: str, tone: str) -> tuple[str, str, str]:
    title = f"{topic}: a practical guide ({(tone or 'technical').split('+')[0].strip()})"
    body = (
        f"# {title}\n\n> Angle: {angle}\n\n## Why now\n{body_core}\n\n"
        f"## How it works\n1. Background\n2. Example\n3. Pitfalls\n\n"
        f"## What to do next\nTry one small experiment and measure the result.\n"
    )
    return title, body, "Subscribe for the next deep dive."
