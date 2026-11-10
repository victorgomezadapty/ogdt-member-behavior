import json
import re
import sys
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
import analysis as A  # noqa: E402

RESULTS = json.loads((ROOT / "reports" / "results.json").read_text(encoding="utf-8"))
HTML = (ROOT / "site" / "index.html").read_text(encoding="utf-8")


class KaplanMeier(unittest.TestCase):
    def test_textbook_example(self):
        # 6 subjects, events at 1, 2, 2 and 4, censored at 3 and 5. At t=2 five are at risk.
        km = A.kaplan_meier(np.array([1, 2, 2, 3, 4, 5]), np.array([1, 1, 1, 0, 1, 0]))
        self.assertAlmostEqual(km["survival"].iloc[0], 5 / 6)
        self.assertAlmostEqual(km["survival"].iloc[1], 5 / 6 * 3 / 5)
        self.assertAlmostEqual(km["survival"].iloc[2], 5 / 6 * 3 / 5 * 1 / 2)

    def test_no_censoring_matches_empirical(self):
        t = np.arange(1, 11)
        km = A.kaplan_meier(t, np.ones(10, int))
        self.assertTrue(np.allclose(km["survival"], 1 - t / 10))

    def test_auc(self):
        self.assertEqual(A.auc(np.array([1, 2, 3, 4]), np.array([0, 0, 1, 1])), 1.0)
        self.assertEqual(A.auc(np.array([1, 1, 1, 1]), np.array([0, 1, 0, 1])), 0.5)


class Results(unittest.TestCase):
    def test_ogdt_consistency(self):
        L = RESULTS["lisboa"]
        self.assertEqual((L["users"], L["dropouts"], L["active"]), (14942, 11968, 2974))
        self.assertEqual(round(L["dropout_share"] * 100, 1), 80.1)

    def test_recompute_from_inputs(self):
        lis = pd.read_csv(ROOT / "data" / "processed" / "lisboa_members.csv")
        car = pd.read_csv(ROOT / "data" / "processed" / "carrera_weekly_visits.csv")
        r = A.run(lis, car, n_boot=20)
        A.checks(r)
        self.assertAlmostEqual(r["lisboa"]["median_months"], RESULTS["lisboa"]["median_months"])
        self.assertAlmostEqual(r["carrera"]["r_week_to_week"], RESULTS["carrera"]["r_week_to_week"])

    def test_page_numbers_match_results(self):
        L, C = RESULTS["lisboa"], RESULTS["carrera"]
        self.assertIn(f"{L['median_months']:.1f} <small>mo", HTML)
        self.assertIn(f"{C['r_week_to_week']:.2f}", HTML)
        self.assertIn(f"{C['r_weeks5_8_to_1_4']:.2f}", HTML)
        self.assertIn(f"AUC of {C['auc_any_weeks1_4']:.2f}", HTML)
        self.assertIn(f"{round(C['p_any_next_given_any'] * 100)}% chance", HTML)
        self.assertIn(f"{L['recency']['median_days_dropouts']:.0f} days", HTML)


class Site(unittest.TestCase):
    def test_local_links_exist(self):
        for href in re.findall(r'href="([^"#:]+)"', HTML):
            self.assertTrue((ROOT / "site" / href).exists(), href)

    def test_no_long_dashes(self):
        for p in list((ROOT / "site").rglob("*.*")) + [ROOT / "README.md"]:
            if p.suffix in {".html", ".js", ".css", ".csv", ".txt", ".md"}:
                text = p.read_text(encoding="utf-8")
                self.assertNotIn("\u2014", text, p)
                self.assertNotIn("\u2013", text, p)


if __name__ == "__main__":
    unittest.main()
