"""Check that every quote in claims/claims.json appears verbatim in its source file
at the pinned commit on GitHub. Needs network. Exit code 1 if any quote is missing."""
from __future__ import annotations

import json
import sys
from pathlib import Path

from .fetch import http

ROOT = Path(__file__).resolve().parent.parent


def main() -> int:
    reg = json.loads((ROOT / "claims" / "claims.json").read_text())
    cache: dict[str, str] = {}
    missing = 0
    for c in reg["claims"]:
        s = reg["sources"][c["source"]]
        url = f"https://raw.githubusercontent.com/{s['repo']}/{s['commit']}/{c['file']}"
        if url not in cache:
            cache[url] = http(url).decode("utf-8", "replace")
        if c["quote"] not in cache[url]:
            missing += 1
            print(f"MISSING {c['id']}: {c['quote']!r} not in {url}")
    print(f"{len(reg['claims']) - missing}/{len(reg['claims'])} quotes found in {len(cache)} pinned files")
    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main())
