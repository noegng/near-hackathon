"""Download raw public data into data/raw/<snapshot>/ without transforming it.

Every source is free and needs no key. Each file is stored exactly as served, and
manifest.json records URL, request body, fetch time and SHA-256, so a reader can
check that the metrics were computed from what the source actually returned.
"""
from __future__ import annotations

import hashlib
import json
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
UA = "near-replicated/0.1 (research; stdlib urllib)"
ARCHIVAL_RPC = "https://archival-rpc.mainnet.fastnear.com"
RPC = "https://rpc.mainnet.fastnear.com"

# name -> URL. One GET each.
HTTP_SOURCES = {
    "llama_intents_volume": "https://api.llama.fi/summary/dexs/near-intents",
    "llama_intents_fees": "https://api.llama.fi/summary/fees/near-intents?dataType=dailyFees",
    "llama_intents_revenue": "https://api.llama.fi/summary/fees/near-intents?dataType=dailyRevenue",
    "llama_intents_holders_revenue": "https://api.llama.fi/summary/fees/near-intents?dataType=dailyHoldersRevenue",
    "llama_near_dexs": "https://api.llama.fi/overview/dexs/near?excludeTotalDataChartBreakdown=true",
    "nearblocks_charts": "https://api.nearblocks.io/v1/charts",
}

DAY = 86400
# NEAR mainnet genesis block and time, used only as the lower bound of the block search.
GENESIS_HEIGHT = 9820210


def http(url: str, body: dict | None = None, tries: int = 6) -> bytes:
    data = json.dumps(body).encode() if body is not None else None
    headers = {"User-Agent": UA, "Accept": "application/json"}
    if data:
        headers["Content-Type"] = "application/json"
    last: Exception | None = None
    for i in range(tries):
        try:
            req = urllib.request.Request(url, data=data, headers=headers)
            with urllib.request.urlopen(req, timeout=60) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            if e.code == 422:  # NEAR RPC answers 422 with a JSON-RPC error body (e.g. UNKNOWN_BLOCK)
                return e.read()
            last = e
            time.sleep((8 if e.code == 429 else 1.5) * (i + 1))
        except Exception as e:  # network errors are retried, then raised
            last = e
            time.sleep(1.5 * (i + 1))
    raise RuntimeError(f"fetch failed: {url}: {last}")


def rpc(method: str, params, archival: bool = True) -> dict:
    time.sleep(0.3)  # public endpoint: stay well under its rate limit
    out = json.loads(http(ARCHIVAL_RPC if archival else RPC,
                          {"jsonrpc": "2.0", "id": 1, "method": method, "params": params}))
    if "error" in out:
        raise RuntimeError(json.dumps(out["error"])[:300])
    return out["result"]


def block_header(block_id) -> dict | None:
    """Header of a block by height, or None when that height was skipped."""
    try:
        return rpc("block", {"block_id": block_id})["header"]
    except RuntimeError as e:
        if "UNKNOWN_BLOCK" in str(e) or "DB Not Found" in str(e):
            return None
        raise


def header_at_or_after(height: int) -> dict:
    for h in range(height, height + 50):
        hd = block_header(h)
        if hd:
            return hd
    raise RuntimeError(f"no block in [{height}, {height + 50})")


def first_block_at(ts_ns: int, lo: dict, hi: dict) -> dict:
    """Header of the first block whose timestamp >= ts_ns, between two known headers.

    Interpolation search: block times are regular enough that guessing the height from
    the two bounding timestamps converges in a few calls instead of ~25 for bisection.
    Requires lo.timestamp < ts_ns <= hi.timestamp.
    """
    while hi["height"] - lo["height"] > 1:
        span_t = hi["timestamp"] - lo["timestamp"]
        frac = (ts_ns - lo["timestamp"]) / span_t
        guess = lo["height"] + int(frac * (hi["height"] - lo["height"]))
        guess = min(max(guess, lo["height"] + 1), hi["height"] - 1)
        hd = header_at_or_after(guess)
        if hd["height"] >= hi["height"]:
            # only skipped heights between guess and hi: walk down instead
            hd = None
            for h in range(guess - 1, lo["height"], -1):
                hd = block_header(h)
                if hd:
                    break
            if hd is None:
                return hi
        if hd["timestamp"] >= ts_ns:
            hi = hd
        else:
            lo = hd
    return hi


def supply_series(end_day: int, days: int, step: int) -> list[dict]:
    """total_supply read from the first block of UTC days, every `step` days, ending at end_day."""
    hi = rpc("block", {"finality": "final"}, archival=False)["header"]
    targets = [end_day - k * step * DAY for k in range(days // step + 1)]
    # lower bound: a block safely older than the oldest target (2 blocks/s is faster than mainnet ever ran)
    span_s = hi["timestamp"] // 10**9 - targets[-1] + 30 * DAY
    lo = header_at_or_after(max(GENESIS_HEIGHT, hi["height"] - 2 * span_s))
    assert lo["timestamp"] < targets[-1] * 10**9, "lower bound is not old enough"
    out = []
    for t in targets:  # newest first, so each result bounds the next search
        hd = first_block_at(t * 10**9, lo, hi)
        out.append({"day": t, "height": hd["height"], "timestamp": hd["timestamp"],
                    "total_supply": hd["total_supply"], "hash": hd["hash"]})
        hi = hd
        print(f"  supply {datetime.fromtimestamp(t, timezone.utc).date()} h={hd['height']}", file=sys.stderr)
    return list(reversed(out))


# NEAR's Intents revenue wallets, as listed in DefiLlama's adapter
# (dimension-adapters/fees/near-intents/index.ts, which cites NEAR's Dune query 6740088).
REVENUE_WALLETS = ("fefundsadmin.sputnik-dao.near", "1csfundsadmin.sputnik-dao.near", "buybacks.multisignature.near")


def rpc_or_none(method: str, params) -> dict | None:
    try:
        return rpc(method, params)
    except RuntimeError as e:
        if "UNKNOWN_ACCOUNT" in str(e) or "does not exist" in str(e):
            return None
        raise


def wallet_balances(points: list[dict]) -> list[dict]:
    """NEAR and wNEAR held by each revenue wallet at the sampled blocks (yoctoNEAR strings, None before creation)."""
    import base64
    out = []
    for p in points:
        row = {"day": p["day"], "height": p["height"], "wallets": {}}
        for w in REVENUE_WALLETS:
            acc = rpc_or_none("query", {"request_type": "view_account", "block_id": p["height"], "account_id": w})
            args = base64.b64encode(json.dumps({"account_id": w}).encode()).decode()
            ft = rpc("query", {"request_type": "call_function", "block_id": p["height"], "account_id": "wrap.near",
                               "method_name": "ft_balance_of", "args_base64": args})
            row["wallets"][w] = {
                "near": None if acc is None else str(int(acc["amount"]) + int(acc["locked"])),
                "wnear": json.loads(bytes(ft["result"]).decode()),
            }
        out.append(row)
        print(f"  wallets {datetime.fromtimestamp(p['day'], timezone.utc).date()}", file=sys.stderr)
    return out


def add_wallets(name: str) -> None:
    """Add rpc_revenue_wallets.json to an existing snapshot, at the blocks of its supply series."""
    out = RAW / name
    manifest = json.loads((out / "manifest.json").read_text())
    raw = json.dumps(wallet_balances(json.loads((out / "rpc_supply.json").read_text())), indent=1).encode()
    (out / "rpc_revenue_wallets.json").write_bytes(raw)
    manifest["files"]["rpc_revenue_wallets"] = {
        "url": ARCHIVAL_RPC, "method": "query view_account + wrap.near ft_balance_of",
        "note": "balances at the same blocks as rpc_supply", "sha256": hashlib.sha256(raw).hexdigest(), "bytes": len(raw)}
    (out / "manifest.json").write_text(json.dumps(manifest, indent=1) + "\n")


def snapshot(name: str | None = None, supply_days: int = 420, supply_step: int = 30) -> Path:
    now = datetime.now(timezone.utc)
    name = name or now.strftime("%Y-%m-%d")
    out = RAW / name
    out.mkdir(parents=True, exist_ok=True)
    manifest = {"snapshot": name, "fetched_at": now.isoformat(timespec="seconds"), "files": {}}

    def save(key: str, raw: bytes, meta: dict):
        (out / f"{key}.json").write_bytes(raw)
        manifest["files"][key] = {**meta, "sha256": hashlib.sha256(raw).hexdigest(), "bytes": len(raw)}
        print(f"saved {key} ({len(raw)} bytes)", file=sys.stderr)

    for key, url in HTTP_SOURCES.items():
        save(key, http(url), {"url": url})

    today = int(now.timestamp()) // DAY * DAY
    series = supply_series(today, supply_days, supply_step)
    save("rpc_supply", json.dumps(series, indent=1).encode(),
         {"url": ARCHIVAL_RPC, "method": "block", "note": "header.total_supply of the first block of each sampled UTC day"})
    for key, method, params in (("rpc_validators", "validators", [None]),
                                ("rpc_protocol_config", "EXPERIMENTAL_protocol_config", {"finality": "final"})):
        body = {"jsonrpc": "2.0", "id": 1, "method": method, "params": params}
        save(key, http(RPC, body), {"url": RPC, "body": body})

    (out / "manifest.json").write_text(json.dumps(manifest, indent=1) + "\n")
    add_wallets(name)
    return out


if __name__ == "__main__":
    print(snapshot(sys.argv[1] if len(sys.argv) > 1 else None))
