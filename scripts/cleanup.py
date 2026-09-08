"""Development-only cleanup (§38): find and remove corrupted prototype rows.

Deletes trend/opportunity/content rows containing URL fragments or leaked
internal text. Cascades handle versions/performance. REFUSES to run when
SIGNALCRAFT_ENV=prod. Dry-run by default; pass --go to apply.

Usage:  python scripts/cleanup.py [--go]
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from signalcraft.content.sanitize import leak_found  # noqa: E402
from signalcraft.db import get_conn  # noqa: E402
from signalcraft.research.normalize import looks_like_url_junk  # noqa: E402


def scan() -> dict[str, list[int]]:
    conn = get_conn()
    try:
        bad_trends = [r["id"] for r in conn.execute("SELECT id, topic FROM trend_signals").fetchall()
                      if looks_like_url_junk(r["topic"] or "")]
        bad_opps = [r["id"] for r in conn.execute(
            "SELECT id, topic, angle FROM content_opportunities").fetchall()
            if looks_like_url_junk(r["topic"] or "") or leak_found(r["angle"] or "")]
        bad_content = [r["id"] for r in conn.execute("SELECT id, body FROM content").fetchall()
                       if leak_found(r["body"] or "")]
        return {"trend_signals": bad_trends, "content_opportunities": bad_opps,
                "content": bad_content}
    finally:
        conn.close()


def main(go: bool = False) -> None:
    if os.getenv("SIGNALCRAFT_ENV", "dev") == "prod":
        raise SystemExit("cleanup refuses to run with SIGNALCRAFT_ENV=prod")
    found = scan()
    total = sum(len(v) for v in found.values())
    for table, ids in found.items():
        print(f"{table}: {len(ids)} corrupt row(s) {ids[:10]}")
    if not go:
        print(f"dry run: {total} row(s) would be deleted (pass --go to apply)")
        return
    conn = get_conn()
    try:
        for table, ids in found.items():
            for rid in ids:
                conn.execute(f"DELETE FROM {table} WHERE id=?", (rid,))
        conn.commit()
    finally:
        conn.close()
    print(f"deleted {total} corrupt row(s)")


if __name__ == "__main__":
    main("--go" in sys.argv)
