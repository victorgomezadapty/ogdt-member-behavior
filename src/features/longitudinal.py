"""Descriptive historical snapshots. Capture remains unverified for this source."""
import numpy as np
import pandas as pd
from src.features.attendance import member_metrics

DIAGNOSTIC_FEATURES = [
    "visits_7d", "visits_30d", "visits_90d", "days_since_last_visit",
    "attendance_frequency_30d", "attendance_frequency_90d",
    "attendance_change_30_vs_previous30", "attendance_pct_change_30_vs_previous30",
    "attendance_change_30_vs_90_baseline", "active_weeks_8w",
    "attendance_variability", "branch_diversity",
]


def observation_cutoffs(checkins):
    """Monthly exclusive boundaries plus the final observed-day boundary."""
    times = checkins.checkin_datetime.dropna()
    if times.empty:
        raise ValueError("Cannot infer descriptive snapshot dates without events")
    final = times.max().normalize() + pd.Timedelta(days=1)
    first = times.min().normalize() + pd.offsets.MonthBegin(1)
    regular = list(pd.date_range(first, final, freq="MS"))
    return pd.DatetimeIndex(sorted(set([*regular, final])))


def longitudinal_metrics(members, checkins, cutoffs):
    dates = pd.DatetimeIndex(cutoffs)
    if dates.empty or dates.has_duplicates or not dates.is_monotonic_increasing:
        raise ValueError("Supply non-empty, unique, increasing exclusive cutoffs")
    frames = []
    for cutoff in dates:
        frame = member_metrics(members, checkins, cutoff)
        # Only use pre-cutoff events to assess even the descriptive time-span bounds.
        history = checkins.loc[checkins.checkin_datetime < cutoff, "checkin_datetime"]
        observed_start = history.min().normalize() if not history.empty else pd.NaT
        frame["export_span_start_as_of"] = observed_start
        for days in [30, 60, 90]:
            frame[f"window_inside_export_span_{days}d"] = bool(pd.notna(observed_start) and cutoff-pd.Timedelta(days=days) >= observed_start)
        frame["consistency_inside_export_span"] = frame.consistency_window_start >= observed_start
        frame["snapshot_boundary"] = "calendar_month_end" if cutoff.day == 1 else "last_observed_date_partial_month"
        frames.append(frame)
    return pd.concat(frames, ignore_index=True)


def eligible_rows(panel, days):
    """Calendar opportunity only; deliberately not named complete/verified exposure."""
    return (panel.sample_observation_status.eq("visits_present_coverage_unverified") &
            panel.membership_tenure_days.ge(days) & panel[f"window_inside_export_span_{days}d"])


def feature_diagnostics(frame):
    represented = frame.sample_observation_status.eq("visits_present_coverage_unverified")
    rows = []
    for feature in DIAGNOSTIC_FEATURES:
        values = frame.loc[represented, feature].dropna()
        rows.append({"feature": feature, "roster_rows": len(frame),
                     "represented_members": int(represented.sum()),
                     "non_null_roster": int(frame[feature].notna().sum()),
                     "non_null_represented": len(values),
                     "null_fraction_roster": float(frame[feature].isna().mean()),
                     "distinct_values_represented": int(values.nunique()),
                     "zero_fraction_of_nonnull_represented": float(values.eq(0).mean()) if len(values) else np.nan,
                     "p25": values.quantile(.25), "median": values.median(),
                     "p75": values.quantile(.75), "minimum": values.min(), "maximum": values.max()})
    return pd.DataFrame(rows)


def summarize_snapshots(panel):
    rows = []
    for cutoff, f in panel.groupby("as_of_exclusive", sort=True):
        represented = f.sample_observation_status.eq("visits_present_coverage_unverified")
        e30, e60, e90 = (eligible_rows(f, days) for days in [30, 60, 90])
        differences = f.loc[e60, "attendance_change_30_vs_previous30"]
        rows.append({"as_of_exclusive": cutoff, "snapshot_boundary": f.snapshot_boundary.iloc[0],
                     "signed_up_roster": len(f), "members_with_exported_history": int(represented.sum()),
                     "no_exported_history": int((~represented).sum()),
                     "calendar_eligible_30d": int(e30.sum()), "calendar_eligible_60d": int(e60.sum()),
                     "calendar_eligible_90d": int(e90.sum()),
                     "median_visits_30d_calendar_eligible": f.loc[e30, "visits_30d"].median(),
                     "median_recency_days_represented": f.loc[represented, "days_since_last_visit"].median(),
                     "positive_30d_count_changes": int(differences.gt(0).sum()),
                     "zero_30d_count_changes": int(differences.eq(0).sum()),
                     "negative_30d_count_changes": int(differences.lt(0).sum()),
                     "median_30d_count_change": differences.median(),
                     "eligible_60d_with_zero_previous30": int(f.loc[e60, "visits_previous30d"].eq(0).sum()),
                     "coverage_verified_members": int(f.coverage_verified.sum())})
    return pd.DataFrame(rows)


def window_sensitivity(frame):
    """Use identical rows to compare two baseline definitions and rate windows."""
    f = frame.loc[eligible_rows(frame, 90)].copy()
    columns = ["member_id", "as_of_exclusive", "synthetic", "coverage_verified",
               "visits_30d", "visits_previous30d", "visits_90d",
               "attendance_change_30_vs_previous30", "attendance_change_30_vs_90_baseline",
               "attendance_frequency_30d", "attendance_frequency_90d"]
    out = f[columns].copy()
    out["baseline_change_sign_agrees"] = np.sign(out.attendance_change_30_vs_previous30) == np.sign(out.attendance_change_30_vs_90_baseline)
    out["frequency_30d_minus_90d"] = out.attendance_frequency_30d - out.attendance_frequency_90d
    # Sign(0) is arithmetic equality, not Stable; no candidate-state label is emitted.
    return out
