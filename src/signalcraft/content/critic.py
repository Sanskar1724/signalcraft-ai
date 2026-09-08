"""Content quality critic (§13). Deterministic rubric, 10 checks, 0-10 score.

Checks: relevance, clarity, originality, hook, readability, platform_fit,
tone, evidence, accuracy-risk, cta. Bounded, no LLM required (LLM critique
is an optional second opinion in generator.py).
"""
from __future__ import annotations

import re


def critique(body: str, platform: str = "LinkedIn", topic: str = "",
             tone: str = "") -> dict:
    text = (body or "").strip()
    words = re.findall(r"[A-Za-z0-9']+", text)
    n = len(words)
    lines = [line for line in text.splitlines() if line.strip()]
    first = lines[0] if lines else ""

    scores: dict[str, float] = {}
    issues: list[str] = []

    # relevance: topic words present
    if topic:
        tset = {w.lower() for w in re.findall(r"[A-Za-z0-9']+", topic) if len(w) > 2}
        hit = len(tset & {w.lower() for w in words})
        scores["relevance"] = min(10.0, 4 + 3 * hit)
    else:
        scores["relevance"] = 7.0
    # clarity: sensible length + structure
    if 40 <= n <= 900:
        scores["clarity"] = 8.0
    elif n < 40:
        scores["clarity"] = 5.0
        issues.append("too short to be useful")
    else:
        scores["clarity"] = 6.0
        issues.append("long — consider tightening")
    # originality: avoid hype cliches
    cliche = sum(text.lower().count(c) for c in ["game-changer", "revolutionize", "unlock the power"])
    scores["originality"] = 8.0 if cliche == 0 else 5.0
    if cliche:
        issues.append("remove generic AI hype phrases")
    # hook: first line short + specific
    scores["hook"] = 8.0 if 20 <= len(first) <= 140 else 5.5
    if scores["hook"] < 7:
        issues.append("tighten hook to one sharp line")
    # readability: paragraphs / threads
    scores["readability"] = 8.0 if len(lines) >= 3 else 6.0
    # platform fit
    pf = 8.0
    if platform == "X" and n > 280:
        pf = 6.5 if "1/" in text else 5.0
        if pf < 7:
            issues.append("X post too long — use a numbered thread")
    if platform == "Blog" and n < 200:
        pf = 5.5
        issues.append("blog too short — add sections and an example")
    if platform == "LinkedIn" and n > 500:
        pf = 6.5
        issues.append("LinkedIn post long — trim to story + 3 takeaways")
    scores["platform_fit"] = pf
    # tone: concrete markers beat fluff
    scores["tone"] = 7.5
    # evidence: numbers, examples, sources
    ev = bool(re.search(r"\d|example|e\.g\.|for instance|source|http", text, re.IGNORECASE))
    scores["evidence"] = 8.0 if ev else 5.0
    if not ev:
        issues.append("add one concrete example or data point")
    # accuracy-risk: hedge invented stats (grounding, §31)
    risky = bool(re.search(r"\d+%|\$\d|\b\d+x\b", text))
    scores["accuracy"] = 6.5 if risky else 8.0
    if risky:
        issues.append("verify any statistics against sources before publishing")
    # cta
    cta = bool(re.search(r"\?|try|subscribe|comment|share|what.*you", text, re.IGNORECASE))
    scores["cta"] = 8.0 if cta else 5.0
    if not cta:
        issues.append("end with a clear CTA or question")

    overall = round(sum(scores.values()) / len(scores), 1)
    # Technical value: composite of evidence, originality and relevance —
    # computed deterministically from the same rubric, never invented.
    scores["technical_value"] = round(
        (scores["evidence"] + scores["originality"] + scores["relevance"]) / 3, 1)
    overall = round(sum(scores.values()) / len(scores), 1)
    if n < 20:
        # Degenerate input: never present a confident score for thin content.
        overall = min(overall, 3.0)
        issues.insert(0, "content too thin to score reliably")
    return {"scores": scores, "overall": overall, "issues": issues,
            "suggestion": "; ".join(issues[:3]) or "Ready to publish."}
