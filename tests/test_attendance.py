"""Regression cases for observation uncertainty and temporal leakage."""
import unittest
import pandas as pd
from src.features.attendance import member_metrics


def events(rows):
    frame = pd.DataFrame(rows, columns=["member_id", "checkin_datetime", "location_id"])
    frame["checkin_datetime"] = pd.to_datetime(frame.checkin_datetime, format="mixed")
    return frame


class AttendanceTests(unittest.TestCase):
    def setUp(self):
        self.cutoff = pd.Timestamp("2024-04-10")
        self.members = pd.DataFrame({"id": [1, 2], "signup_date": [self.cutoff - pd.Timedelta(days=150)] * 2})

    def test_half_open_edges_and_future_only_member(self):
        c = events([(1, self.cutoff-pd.Timedelta(days=d), 1) for d in [90, 60, 30, 7, 1]] +
                   [(1, self.cutoff-pd.Timedelta(days=7)-pd.Timedelta(nanoseconds=1), 1),
                    (1, self.cutoff, 1), (1, self.cutoff+pd.Timedelta(days=1), 1),
                    (2, self.cutoff, 1)])
        f = member_metrics(self.members, c, self.cutoff).set_index("member_id")
        self.assertEqual(f.loc[1, "visits_7d"], 2)
        self.assertEqual(f.loc[1, "visits_30d"], 4)
        self.assertEqual(f.loc[1, "visits_90d"], 6)
        self.assertEqual(f.loc[1, "visits_previous30d"], 1)
        self.assertEqual(f.loc[1, "attendance_change_30_vs_90_baseline"], 3)
        self.assertEqual(f.loc[1, "days_since_last_visit"], 1)
        self.assertTrue(pd.isna(f.loc[2, "visits_30d"]))
        self.assertEqual(f.loc[2, "sample_observation_status"], "no_visits_in_public_sample")

    def test_unknown_is_not_recent_zero(self):
        c = events([(1, self.cutoff-pd.Timedelta(days=100), 1)])
        f = member_metrics(self.members, c, self.cutoff).set_index("member_id")
        self.assertEqual(f.loc[1, "visits_30d"], 0)
        self.assertEqual(f.loc[1, "attendance_variability"], 0)
        self.assertTrue(pd.isna(f.loc[1, "attendance_pct_change_30_vs_previous30"]))
        for col in ["visits_7d", "visits_30d", "visits_90d", "active_weeks_8w", "attendance_variability", "branch_diversity", "days_since_last_visit"]:
            self.assertTrue(pd.isna(f.loc[2, col]), col)
        self.assertFalse(f.coverage_verified.any())

    def test_new_member_counts_retained_but_full_window_metrics_unavailable(self):
        m = self.members.copy()
        m.loc[m.id == 1, "signup_date"] = self.cutoff-pd.Timedelta(days=10)
        c = events([(1, self.cutoff-pd.Timedelta(days=1), 1)])
        f = member_metrics(m, c, self.cutoff).set_index("member_id")
        self.assertEqual(f.loc[1, "visits_30d"], 1)
        self.assertFalse(f.loc[1, "full_tenure_30d"])
        for col in ["attendance_frequency_30d", "attendance_change_30_vs_previous30", "attendance_change_30_vs_90_baseline", "active_weeks_8w"]:
            self.assertTrue(pd.isna(f.loc[1, col]), col)

    def test_complete_weeks_exclude_current_partial_week(self):
        c = events([(1, "2024-02-12", 1), (1, "2024-04-07 23:59", 1),
                    (1, "2024-04-08", 1), (1, "2024-04-09", 1)])
        f = member_metrics(self.members, c, self.cutoff).set_index("member_id")
        self.assertEqual(f.loc[1, "consistency_window_start"], pd.Timestamp("2024-02-12"))
        self.assertEqual(f.loc[1, "consistency_window_end_exclusive"], pd.Timestamp("2024-04-08"))
        self.assertEqual(f.loc[1, "active_weeks_8w"], 2)

    def test_contract_outcomes_do_not_change_behavior_features(self):
        c = events([(1, self.cutoff-pd.Timedelta(days=1), 1)])
        m = self.members.assign(cancel_date=pd.Timestamp("2024-01-01"), is_active=False, cancel_reason="anything")
        pd.testing.assert_frame_equal(member_metrics(self.members, c, self.cutoff), member_metrics(m, c, self.cutoff))

    def test_preferences_preserve_ties_and_branch_support(self):
        c = events([(1, "2024-04-01 07:00", 1), (1, "2024-04-02 18:00", 2)])
        f = member_metrics(self.members, c, self.cutoff).set_index("member_id")
        self.assertEqual(f.loc[1, "preferred_day"], "Monday|Tuesday")
        self.assertEqual(f.loc[1, "preferred_time"], "evening_17_22|morning_05_12")
        self.assertEqual(f.loc[1, "branch_diversity"], 2)
        self.assertEqual(f.loc[1, "preference_visit_support_90d"], 2)

    def test_reject_ambiguous_cutoff_clock(self):
        c = events([(1, "2024-04-01", 1)])
        for cutoff in ["2024-04-10T01:00", "2024-04-10T00:00Z"]:
            with self.assertRaises(ValueError):
                member_metrics(self.members, c, cutoff)


if __name__ == "__main__":
    unittest.main()
