import math
import re
import unittest
from pathlib import Path

from replicated import build, page

ROOT = Path(__file__).resolve().parent.parent


class Page(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = page.render(build.thesis_snapshot())

    def test_committed_page_is_what_the_build_renders(self):
        self.assertEqual((ROOT / "docs" / "index.html").read_text(), self.html)

    def test_page_is_self_contained(self):
        """No scripts, styles, fonts or images are loaded from elsewhere; links to sources are allowed."""
        self.assertFalse(re.findall(r'<(?:script|img|link|iframe)[^>]*\s(?:src|href)=', self.html))
        self.assertNotIn("@import", self.html)
        self.assertNotIn("url(", self.html)

    def test_no_broken_numbers(self):
        for bad in ("nan", "NaN", "inf", "None"):
            self.assertNotRegex(self.html, rf'[">,\s]{bad}[",<\s%]')

    def test_charts_and_tables_are_present(self):
        self.assertEqual(self.html.count("<svg"), 5)
        self.assertGreaterEqual(self.html.count("<table"), 4)
        self.assertEqual(self.html.count("<polyline"), 4)

    def test_helpers(self):
        self.assertEqual(page.money(125_257_736), "$125M")
        self.assertEqual(page.money(3.76e9), "$3.8B")
        self.assertEqual(page.count(657_883), "658K")
        self.assertEqual(page.nice_max(19.8), 20)
        self.assertEqual(page.nice_max(4.36e6), 4.8e6)
        self.assertEqual(page.month_label("2026-11-11"), "Nov 26")

    def test_axis_ticks_need_no_rounding(self):
        """The four tick labels are quarters of the axis top; with one or two digits they must be exact."""
        for v in (0.9, 1.97, 7.6, 23.1, 98, 4.36e6, 7.4e6, 1.6e8):
            top = page.nice_max(v)
            self.assertGreaterEqual(top, v)
            lead = top / 4 / 10 ** (math.floor(math.log10(top)) - 1)
            self.assertAlmostEqual(lead, round(lead), places=6, msg=f"{v} -> {top}")

    def test_labels_do_not_overlap(self):
        out = page.spread([100.0, 104.0], 15)
        self.assertGreaterEqual(abs(out[1] - out[0]), 15)
        self.assertLess(out[0], out[1])
        self.assertAlmostEqual(sum(out), 204.0)
        self.assertEqual(page.spread([10.0, 90.0], 15), [10.0, 90.0])


if __name__ == "__main__":
    unittest.main()
