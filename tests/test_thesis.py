"""THESIS.md may only quote numbers the build produces: every row of its evidence table
must equal the computed metric, and every figure used in the prose must appear in that table."""
import re
import unittest
from pathlib import Path

from replicated import build, metrics

ROOT = Path(__file__).resolve().parent.parent


def parse(value: str) -> tuple[float, float]:
    """Returns (number, half a unit of its last shown digit)."""
    v = value.replace("NEAR", "").replace("years", "").strip()
    mult = 1.0
    if v.startswith("$"):
        v = v[1:]
    if v.endswith("B"):
        mult, v = 1e9, v[:-1]
    elif v.endswith("M"):
        mult, v = 1e6, v[:-1]
    num = v.rstrip("%x").replace(",", "")
    decimals = len(num.split(".")[1]) if "." in num else 0
    return float(num) * mult, 0.5 * 10 ** -decimals * mult


class Thesis(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = (ROOT / "THESIS.md").read_text()
        cls.m = metrics.compute(build.load_raw(build.thesis_snapshot()))["metrics"]
        table = cls.text.split("## Evidence table")[1]
        cls.rows = re.findall(r"^\| `(\w+)` \| ([^|]+) \|", table, re.M)

    def test_evidence_table_matches_computation(self):
        self.assertGreaterEqual(len(self.rows), 30)
        for mid, shown in self.rows:
            (got, half), want = parse(shown), self.m[mid]["value"]
            # the text may round, never more than half a unit of the last digit it shows
            self.assertAlmostEqual(got, want, delta=half * 1.001, msg=f"{mid}: THESIS says {shown}, build says {want}")

    def test_prose_figures_come_from_the_table(self):
        prose = self.text.split("## Evidence table")[0]
        for mid, shown in self.rows:
            self.assertIn(shown.strip(), prose, f"{mid} is in the evidence table but not used in the text")


if __name__ == "__main__":
    unittest.main()
