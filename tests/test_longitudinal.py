import unittest
import pandas as pd
from src.features.longitudinal import longitudinal_metrics, observation_cutoffs, summarize_snapshots, window_sensitivity


def visits(rows):
    frame = pd.DataFrame(rows, columns=["member_id", "checkin_datetime", "location_id"])
    frame["checkin_datetime"] = pd.to_datetime(frame.checkin_datetime, format="mixed")
    return frame


class LongitudinalTests(unittest.TestCase):
    def setUp(self):
        self.members = pd.DataFrame({"id": [1, 2, 3], "signup_date": pd.to_datetime(["2023-01-01", "2023-03-01", "2023-07-01"])})
        self.events = visits([(1, "2023-01-15", 1), (1, "2023-04-01", 1), (2, "2023-05-01", 2)])

    def test_future_records_cannot_change_earlier_snapshot_or_support(self):
        cuts = ["2023-04-01", "2023-06-01"]
        historical = longitudinal_metrics(self.members, self.events, cuts)
        appended = pd.concat([self.events, visits([(1, "2023-06-15", 2), (3, "2023-07-05", 1)])], ignore_index=True)
        pd.testing.assert_frame_equal(historical, longitudinal_metrics(self.members, appended, cuts))
        # Future-only member 2 exists in roster but remains unknown at April's cutoff.
        early = historical[historical.as_of_exclusive.eq(pd.Timestamp("2023-04-01"))]
        self.assertTrue(early.loc[early.member_id.eq(2), "visits_30d"].isna().all())
        self.assertNotIn(3, historical.member_id.tolist())

    def test_span_boundary_is_not_full_capture(self):
        panel = longitudinal_metrics(self.members, self.events, ["2023-02-01", "2023-06-01"])
        early = panel[panel.as_of_exclusive.eq(pd.Timestamp("2023-02-01"))]
        self.assertFalse(early.window_inside_export_span_30d.any())
        self.assertFalse(panel.coverage_verified.any())
        summary = summarize_snapshots(panel)
        self.assertEqual(summary.iloc[0].calendar_eligible_30d, 0)
        self.assertEqual(summary.iloc[1].calendar_eligible_90d, 2)
        self.assertTrue(summary.coverage_verified_members.eq(0).all())

    def test_month_cutoffs_do_not_create_future_full_month(self):
        dates = observation_cutoffs(self.events)
        self.assertEqual(dates[0], pd.Timestamp("2023-02-01"))
        self.assertEqual(dates[-1], pd.Timestamp("2023-05-02"))
        self.assertNotIn(pd.Timestamp("2023-06-01"), dates)

    def test_sign_comparison_keeps_identical_eligible_members(self):
        panel = longitudinal_metrics(self.members, self.events, ["2023-06-01"])
        compared = window_sensitivity(panel)
        self.assertEqual(set(compared.member_id), {1, 2})
        signs = compared.set_index("member_id").baseline_change_sign_agrees
        self.assertFalse(signs.loc[1])  # Zero against previous30; negative against prior60 baseline.
        self.assertTrue(signs.loc[2])
        self.assertFalse(compared.coverage_verified.any())

    def test_invalid_snapshot_sequence_rejected(self):
        for dates in [[], ["2023-06-01", "2023-04-01"], ["2023-04-01", "2023-04-01"]]:
            with self.assertRaises(ValueError):
                longitudinal_metrics(self.members, self.events, dates)

    def test_empty_pre_cutoff_history_does_not_invent_zeros(self):
        panel = longitudinal_metrics(self.members, self.events, ["2023-01-10"])
        self.assertEqual(panel.member_id.tolist(), [1])
        self.assertTrue(panel.visits_30d.isna().all())
        self.assertFalse(panel.window_inside_export_span_30d.any())
        empty = longitudinal_metrics(self.members, self.events, ["2023-01-01"])
        self.assertTrue(empty.empty)


if __name__ == "__main__":
    unittest.main()
