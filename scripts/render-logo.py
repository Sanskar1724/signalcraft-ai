"""Render brand SVGs to PNGs (dev utility). Requires: python -m pip install resvg-py."""
from __future__ import annotations

import sys
from pathlib import Path

from resvg_py import svg_to_bytes

ROOT = Path(__file__).resolve().parents[1]
PUB = ROOT / "apps" / "web" / "public"


def render(name: str, width: int, height: int | None = None) -> Path:
    src = PUB / f"{name}.svg"
    out = PUB / f"{name}.png"
    kw = {"width": width}
    if height:
        kw["height"] = height
    out.write_bytes(svg_to_bytes(src.read_text(encoding="utf-8"), **kw))
    print(f"{out.name}: {out.stat().st_size // 1024} KB")
    return out


if __name__ == "__main__":
    render("logo", 1024, 1024)
    render("logo-lockup", 1280)
    render("og-image", 1200, 630)
