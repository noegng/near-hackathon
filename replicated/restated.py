"""Compare two raw snapshots day by day: which past daily values did a source change?

Usage: python3 -m replicated.restated <older> <newer>
"""
from __future__ import annotations

import math
import sys

from . import build, metrics

SERIES = ("llama_intents_volume", "llama_intents_fees", "llama_intents_revenue")


def diff(old: dict[int, float], new: dict[int, float]) -> dict:
    common = sorted(set(old) & set(new))
    changed = [(d, old[d], new[d]) for d in common if old[d] != new[d]]
    return {"days_compared": len(common), "days_changed": len(changed),
            "sum_old": math.fsum(old[d] for d in common), "sum_new": math.fsum(new[d] for d in common), "changed": changed}


def main(argv: list[str]) -> int:
    a, b = build.load_raw(argv[1]), build.load_raw(argv[2])
    for key in SERIES:
        r = diff(metrics.llama_series(a[key]), metrics.llama_series(b[key]))
        print(f"{key}: {r['days_changed']} of {r['days_compared']} days changed, total {r['sum_old']:,.0f} -> {r['sum_new']:,.0f}")
        for d, x, y in r["changed"][-10:]:
            print(f"   {metrics.datetime.fromtimestamp(d, metrics.timezone.utc).date()}  {x:,.0f} -> {y:,.0f}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
