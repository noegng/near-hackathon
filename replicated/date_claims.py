"""Record when each claim was published: the commit that wrote its quote.

For every claim, walk back through the commits that changed its file, from the pinned commit,
while the quote is still present; the oldest of them wrote the number. Its author date is the
publication date that replicated.compare compares the claim on. Needs git and network: it clones
each source repository (without checking files out) into a temporary directory, runs no code from
it, and rewrites the `published` field of every claim in claims/claims.json.
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REGISTRY = ROOT / "claims" / "claims.json"


def git(repo: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True, text=True).stdout


def clone_url(src: dict) -> str:
    host = "gitlab.com" if src.get("host") == "gitlab" else "github.com"
    return f"https://{host}/{src['repo']}.git"


def writing_commit(repo: Path, pinned: str, file: str, quote: str) -> str:
    """Oldest commit of the unbroken run, ending at `pinned`, whose `file` contains `quote`."""
    found = None
    for rev in git(repo, "rev-list", pinned, "--", file).split():
        if quote not in git(repo, "show", f"{rev}:{file}"):
            break
        found = rev
    if found is None:
        raise ValueError(f"quote not found at {pinned}:{file}: {quote!r}")
    return found


def utc(iso: str) -> str:
    return datetime.fromisoformat(iso.replace("Z", "+00:00")).astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def main() -> int:
    reg = json.loads(REGISTRY.read_text())
    with tempfile.TemporaryDirectory() as tmp:
        for key, src in reg["sources"].items():
            repo = Path(tmp) / key
            subprocess.run(["git", "clone", "--quiet", "--no-checkout", clone_url(src), str(repo)], check=True)
            for c in (c for c in reg["claims"] if c["source"] == key):
                sha = writing_commit(repo, src["commit"], c["file"], c["quote"])
                c["published"] = {"commit": sha, "date": utc(git(repo, "show", "-s", "--format=%aI", sha).strip())}
            print(f"{key}: {sum(c['source'] == key for c in reg['claims'])} claims dated")
    REGISTRY.write_text(json.dumps(reg, indent=1, ensure_ascii=True) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
