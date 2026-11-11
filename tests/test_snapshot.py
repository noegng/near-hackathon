"""Checks on the committed raw snapshots: integrity, and agreement between independent sources."""
import hashlib
import json
import unittest
from pathlib import Path

from replicated import build, metrics as M

RAW = Path(__file__).resolve().parent.parent / "data" / "raw"
SNAPSHOTS = sorted(p.name for p in RAW.iterdir() if p.is_dir())


class Snapshot(unittest.TestCase):
    def test_files_match_manifest_hashes(self):
        for snap in SNAPSHOTS:
            man = json.loads((RAW / snap / "manifest.json").read_text())
            for key, meta in man["files"].items():
                raw = (RAW / snap / f"{key}.json").read_bytes()
                self.assertEqual(hashlib.sha256(raw).hexdigest(), meta["sha256"], f"{snap}/{key}")

    def test_rpc_supply_blocks_start_their_utc_day(self):
        for snap in SNAPSHOTS:
            for p in json.loads((RAW / snap / "rpc_supply.json").read_text()):
                offset = p["timestamp"] // 10**9 - p["day"]
                self.assertTrue(0 <= offset < 10, f"{snap}: block {p['height']} is {offset}s after midnight")

    def test_block_header_supply_agrees_with_nearblocks(self):
        """Two independent readings of total supply (archival RPC, NearBlocks) agree within 0.001%."""
        for snap in SNAPSHOTS:
            raw = build.load_raw(snap)
            nb = M.nearblocks_series(raw["nearblocks_charts"])["supply_near"]
            checked = 0
            for p in raw["rpc_supply"]:
                # NearBlocks stamps a day with its end-of-day supply; RPC reads the first block of the next day.
                d = p["day"] - M.DAY
                if d in nb:
                    self.assertAlmostEqual(nb[d] / (int(p["total_supply"]) / M.YOCTO), 1.0, delta=1e-5, msg=f"{snap} {d}")
                    checked += 1
            self.assertGreaterEqual(checked, 10)

    def test_our_30d_sums_match_defillama_own_totals(self):
        for snap in SNAPSHOTS:
            raw = build.load_raw(snap)
            for key in ("llama_intents_volume", "llama_intents_fees", "llama_intents_revenue"):
                s = M.llama_series(raw[key])
                self.assertAlmostEqual(M.wsum(s, max(s), 30), raw[key]["total30d"], delta=1.0, msg=f"{snap}/{key}")

    def test_build_is_deterministic(self):
        raw = build.load_raw(SNAPSHOTS[-1])
        self.assertEqual(json.dumps(M.compute(raw), sort_keys=True), json.dumps(M.compute(raw), sort_keys=True))


if __name__ == "__main__":
    unittest.main()
