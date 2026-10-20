import unittest
import numpy as np
import pandas as pd
from src.data.berkeley import DATASET_ID, TABLE_SHA256, monthly_observations, assert_same_population
from src.features.monthly import monthly_metrics, OUTPUT_COLUMNS


def observations(rows):
    frame = pd.DataFrame(rows, columns=["member_id", "period_end", "attendance_eligible", "recorded_attendance_month"])
    frame["period_end"] = pd.to_datetime(frame.period_end)
    frame["member_id"] = frame.member_id.astype(str)
    frame["dataset_id"] = DATASET_ID
    frame["club_id"] = 11
    return frame


class MonthlyTests(unittest.TestCase):
    def test_calendar_windows_keep_recorded_zeros(self):
        f = monthly_metrics(observations([(1,"1997-04-30",True,6), (1,"1997-05-31",True,0), (1,"1997-06-30",True,0)]))
        self.assertTrue(pd.isna(f.iloc[0].attendance_previous_month))
        june = f.iloc[-1]
        self.assertEqual(june.attendance_sum_3_calendar_months, 6)
        self.assertEqual(june.attendance_mean_3_calendar_months, 2)
        self.assertEqual(june.positive_attendance_months_3, 1)
        self.assertEqual(june.months_since_recorded_positive_month, 2)
        self.assertTrue(pd.isna(june.attendance_pct_change_vs_previous_month))
        self.assertTrue(pd.isna(june.attendance_sum_6_calendar_months))
        self.assertEqual(june.as_of_exclusive, pd.Timestamp("1997-07-01"))

    def test_missing_calendar_row_breaks_history(self):
        f = monthly_metrics(observations([(1,"1997-04-30",True,4), (1,"1997-06-30",True,0)]))
        self.assertTrue(pd.isna(f.iloc[-1].attendance_previous_month))
        self.assertEqual(f.iloc[-1].consecutive_eligible_months, 1)
        self.assertTrue(pd.isna(f.iloc[-1].months_since_recorded_positive_month))

    def test_ineligible_high_value_cannot_bridge_a_window(self):
        f = monthly_metrics(observations([(1,"1997-04-30",True,4), (1,"1997-05-31",False,999), (1,"1997-06-30",True,2), (1,"1997-07-31",True,0)]))
        self.assertEqual(len(f), 3)
        self.assertTrue(pd.isna(f.iloc[1].attendance_previous_month))
        self.assertTrue(f.attendance_sum_3_calendar_months.isna().all())
        self.assertEqual(f.iloc[-1].consecutive_eligible_months, 2)
        self.assertEqual(f.iloc[-1].months_since_recorded_positive_month, 1)

    def test_future_rows_and_unrelated_members_cannot_change_past(self):
        base = observations([(1,"1997-04-30",True,3), (1,"1997-05-31",True,2)])
        added = observations([(1,"1997-06-30",True,42), (2,"1997-04-30",True,40)])
        combined = monthly_metrics(pd.concat([base, added], ignore_index=True))
        same = combined[combined.member_id.eq("1") & combined.period_end.lt("1997-06-01")].reset_index(drop=True)
        pd.testing.assert_frame_equal(monthly_metrics(base), same)
        forbidden = {"endatt", "endcont", "endcontp", "overtime", "problem", "birthday", "churn_probability", "visits_30d", "days_since_last_visit"}
        self.assertFalse(forbidden.intersection(combined))

    def test_overtime_positive_attendance_is_not_an_observed_zero(self):
        def day(s):
            return pd.Timestamp(s).to_pydatetime().toordinal() + 366
        raw = pd.DataFrame({"id":[1,1,1], "time":[day("2000-07-01"),day("2000-08-01"),day("2000-09-01")],
                            "attend":[3,12,0], "contract":[1,1,7], "club":[11]*3,
                            "duplicate":[0]*3,"problem":[0]*3,"overtime":[0,1,1],
                            "begatt":[day("1997-04-01")]*3,"endatt":[day("2000-08-01")]*3})
        audit = monthly_observations(raw)
        self.assertEqual(audit.attendance_eligible.tolist(), [True,False,False])
        self.assertTrue(audit.loc[1:, "recorded_attendance_month"].isna().all())
        self.assertEqual(monthly_metrics(audit).recorded_attendance_month.tolist(), [3])

    def test_namespaced_population_and_full_key_required(self):
        key = pd.DataFrame({"dataset_id":[DATASET_ID],"member_id":["1"],"period_end":["1997-04-30"]})
        self.assertEqual(len(assert_same_population(key,key,TABLE_SHA256,TABLE_SHA256)),1)
        for other in [key.assign(dataset_id="mindweave/gym-memberships"), key.drop(columns="period_end"), pd.concat([key,key])]:
            with self.assertRaises(ValueError):
                assert_same_population(key,other,TABLE_SHA256,TABLE_SHA256)
        with self.assertRaises(ValueError):
            assert_same_population(key,key,TABLE_SHA256,"different_table")

    def test_duplicate_keys_and_non_month_end_rejected(self):
        f = observations([(1,"1997-04-30",True,1)])
        with self.assertRaises(ValueError):
            monthly_metrics(pd.concat([f,f]))
        with self.assertRaises(ValueError):
            monthly_metrics(f.assign(period_end=pd.Timestamp("1997-04-15")))

    def test_all_zero_left_edge_does_not_invent_last_positive_month(self):
        f = monthly_metrics(observations([(1,"1997-04-30",True,0), (1,"1997-05-31",True,0), (1,"1997-06-30",True,0)]))
        self.assertTrue(f.months_since_recorded_positive_month.isna().all())
        self.assertEqual(f.iloc[-1].attendance_std_3_calendar_months,0)
        self.assertEqual(f.iloc[-1].attendance_sum_3_calendar_months,0)

    def test_all_ineligible_input_returns_empty_output_not_zero_rows(self):
        f = monthly_metrics(observations([(1,"2000-08-31",False,12)]))
        self.assertTrue(f.empty)
        self.assertEqual(list(f.columns), OUTPUT_COLUMNS)

    def test_fractional_recorded_attendance_rejected(self):
        with self.assertRaises(ValueError):
            monthly_metrics(observations([(1,"1997-04-30",True,1.5)]))


if __name__ == "__main__":
    unittest.main()
