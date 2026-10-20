"""Calendar-month behavior; unavailable months break histories instead of becoming zero."""
import numpy as np
import pandas as pd
from src.data.berkeley import DATASET_ID, KEY, POLICY_ID

FEATURE_COLUMNS = ["recorded_attendance_month", "attendance_previous_month", "attendance_change_vs_previous_month",
                   "attendance_pct_change_vs_previous_month", "attendance_sum_3_calendar_months",
                   "attendance_mean_3_calendar_months", "attendance_std_3_calendar_months",
                   "positive_attendance_months_3", "attendance_sum_6_calendar_months",
                   "attendance_mean_6_calendar_months", "consecutive_eligible_months",
                   "months_since_recorded_positive_month"]
OUTPUT_COLUMNS = KEY + ["club_id", "as_of_exclusive", "synthetic", "selection_policy_id", "availability_basis", "coverage_basis"] + FEATURE_COLUMNS


def monthly_metrics(observations):
    needed = set(KEY + ["club_id", "attendance_eligible", "recorded_attendance_month"])
    if not needed.issubset(observations) or observations[list(needed)].drop(columns="recorded_attendance_month").isna().any().any():
        raise ValueError("Complete monthly identity and eligibility are required")
    if not observations.dataset_id.eq(DATASET_ID).all() or observations.duplicated(KEY).any():
        raise ValueError("Use one namespaced Berkeley row per member/month")
    out = observations[list(needed)].copy().sort_values(["member_id", "period_end"]).reset_index(drop=True)
    out["period_end"] = pd.to_datetime(out.period_end)
    if not out.period_end.eq(out.period_end.dt.to_period("M").dt.to_timestamp("M")).all():
        raise ValueError("period_end must be a calendar month-end date")
    if not out.attendance_eligible.isin([True, False]).all():
        raise ValueError("Eligibility must be explicit")
    eligible = out.attendance_eligible
    if out.loc[eligible, "recorded_attendance_month"].isna().any() or (out.loc[eligible, "recorded_attendance_month"] < 0).any():
        raise ValueError("Eligible months require valid recorded attendance")
    counts = out.loc[eligible, "recorded_attendance_month"]
    if not np.isfinite(counts).all() or not counts.eq(np.floor(counts)).all():
        raise ValueError("Monthly attendance must be finite nonnegative integer counts")
    out.loc[~eligible, "recorded_attendance_month"] = np.nan
    ordinal = out.period_end.dt.to_period("M").astype("int64")
    previous_period = ordinal.groupby(out.member_id).shift()
    previous_eligible = eligible.groupby(out.member_id).shift(fill_value=False)
    continuous = ordinal.sub(previous_period).eq(1) & eligible & previous_eligible
    # A missing calendar row and an explicit ineligible month both break the run.
    breaks = (~continuous).astype(int).groupby(out.member_id).cumsum()
    out["attendance_previous_month"] = out.recorded_attendance_month.groupby(out.member_id).shift().where(continuous)
    # Avoid rolling through hundreds of thousands of ineligible calendar-padding groups.
    out = out.loc[eligible].copy()
    if out.empty:
        return pd.DataFrame(columns=OUTPUT_COLUMNS)
    ordinal = ordinal.loc[out.index]
    groups = [out.member_id, breaks.loc[out.index]]
    out["consecutive_eligible_months"] = out.groupby(groups, sort=False).cumcount() + 1
    out["attendance_change_vs_previous_month"] = out.recorded_attendance_month - out.attendance_previous_month
    out["attendance_pct_change_vs_previous_month"] = out.recorded_attendance_month / out.attendance_previous_month.replace(0, np.nan) - 1
    for length in [3, 6]:
        rolling = out.groupby(groups, sort=False).recorded_attendance_month.rolling(length, min_periods=length)
        out[f"attendance_sum_{length}_calendar_months"] = rolling.sum().reset_index(level=[0, 1], drop=True).reindex(out.index)
        out[f"attendance_mean_{length}_calendar_months"] = out[f"attendance_sum_{length}_calendar_months"] / length
        if length == 3:
            out["attendance_std_3_calendar_months"] = rolling.std(ddof=0).reset_index(level=[0, 1], drop=True).reindex(out.index)
            positive = out.recorded_attendance_month.gt(0)
            out["positive_attendance_months_3"] = positive.groupby(groups, sort=False).rolling(3, min_periods=3).sum().reset_index(level=[0, 1], drop=True).reindex(out.index)
    last_positive_period = ordinal.where(out.recorded_attendance_month.gt(0)).groupby(groups, sort=False).ffill()
    out["months_since_recorded_positive_month"] = ordinal.sub(last_positive_period)
    out["as_of_exclusive"] = out.period_end + pd.Timedelta(days=1)
    out["synthetic"] = False
    out["selection_policy_id"] = POLICY_ID
    out["availability_basis"] = "assumed_month_close_no_ingestion_clock"
    out["coverage_basis"] = "author_flags_and_documented_month_span"
    # Diagnostic exclusion flags, contract endpoints, prices and demographics are absent.
    return out[OUTPUT_COLUMNS].reset_index(drop=True)
