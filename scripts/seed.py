"""Seed realistic demo data (§27). Clearly fake: profile is 'Demo Creator',
research comes from the labeled sample source. Idempotent-ish: skips when
content already exists unless --fresh is passed.

Usage:  python scripts/seed.py [--fresh]
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from signalcraft import analytics, calendar  # noqa: E402
from signalcraft.content.generator import generate_content  # noqa: E402
from signalcraft.db import get_conn, init_db  # noqa: E402
from signalcraft.memory import learn_from_performance  # noqa: E402
from signalcraft.opportunities import build_opportunities  # noqa: E402
from signalcraft.profiles import seed_default_profile  # noqa: E402
from signalcraft.research import collect_and_store  # noqa: E402
from signalcraft.taxonomy import sync_profile_taxonomy  # noqa: E402

PLATFORMS = ["LinkedIn", "X", "Blog"]


def _h(*parts: str) -> int:
    return int(hashlib.md5("|".join(parts).encode()).hexdigest(), 16)


def main(fresh: bool = False) -> None:
    if fresh:
        db = ROOT / "data" / "signalcraft.db"
        for suffix in ("", "-wal", "-shm"):
            Path(str(db) + suffix).unlink(missing_ok=True)
    init_db()
    conn = get_conn()
    try:
        conn.execute("UPDATE users SET name='Demo Creator' WHERE id=1")
        conn.commit()
        existing = conn.execute("SELECT COUNT(*) AS n FROM content").fetchone()["n"]
    finally:
        conn.close()
    if existing and not fresh:
        print(f"seed: {existing} content rows already present, skipping (use --fresh)")
        return

    seed_default_profile()
    sync_profile_taxonomy()
    collect_and_store(limit=20, use_live=False)
    opps = build_opportunities()
    made = 0
    for opp in opps[:7]:
        for plat in PLATFORMS:
            res = generate_content(opp["id"], platform=plat)
            cid = res["content"]["id"]
            imp = 500 + _h(opp["topic"], plat) % 4500
            eng = 2 + _h(plat, opp["topic"], "e") % 9  # 2-10%
            likes = int(imp * eng / 100 * 0.7)
            rest = int(imp * eng / 100 * 0.3)
            analytics.record_performance(
                cid, platform=plat, impressions=imp, likes=likes,
                comments=rest // 3, shares=rest // 3, saves=rest // 3,
                clicks=rest // 6, reach=int(imp * 0.8))
            made += 1
    calendar.schedule(1, "LinkedIn", "2026-09-10 10:00", notes="Demo: repurpose top topic")
    calendar.schedule(1, "X", "2026-09-11 10:00", notes="Demo: thread version")
    print(f"seed: creator=Demo Creator content={made} learn={learn_from_performance()}")


if __name__ == "__main__":
    main("--fresh" in sys.argv)
