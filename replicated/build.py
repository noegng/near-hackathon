"""One command: read a raw snapshot, write out/metrics.json. No network access."""
from __future__ import annotations

import json
import sys
from pathlib import Path

from . import metrics

ROOT = Path(__file__).resolve().parent.parent


def load_raw(snapshot: str) -> dict:
    d = ROOT / "data" / "raw" / snapshot
    return {p.stem: json.loads(p.read_text()) for p in sorted(d.glob("*.json")) if p.stem != "manifest"}


def latest_snapshot() -> str:
    return sorted(p.name for p in (ROOT / "data" / "raw").iterdir() if p.is_dir())[-1]


def main(argv: list[str]) -> int:
    snap = argv[1] if len(argv) > 1 else latest_snapshot()
    result = {"snapshot": snap, **metrics.compute(load_raw(snap))}
    out = ROOT / "out"
    out.mkdir(exist_ok=True)
    (out / "metrics.json").write_text(json.dumps(result, indent=1) + "\n")
    print(f"snapshot {snap}, asof {result['asof']}: {len(result['metrics'])} metrics -> out/metrics.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
