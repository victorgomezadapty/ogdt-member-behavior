"""Half-open as-of windows; sample absence is never labeled inactivity."""
import numpy as np
import pandas as pd


def member_metrics(members, checkins, cutoff):
    cutoff = pd.Timestamp(cutoff)
    if cutoff.tzinfo is not None or cutoff != cutoff.normalize():
        raise ValueError("Use a timezone-naive midnight exclusive cutoff for this source")
    m = members.loc[members.signup_date < cutoff, ["id", "signup_date"]].set_index("id")
    c = checkins.loc[checkins.checkin_datetime < cutoff].copy()
    c = c[c.member_id.isin(m.index)]
    out = pd.DataFrame(index=m.index)
    out.index.name = "member_id"
    out["as_of_exclusive"] = cutoff
    out["synthetic"] = True
    out["coverage_verified"] = False
    observed = out.index.isin(c.member_id.unique())
    out["sample_observation_status"] = np.where(observed, "visits_present_coverage_unverified", "no_visits_in_public_sample")
    out["membership_tenure_days"] = (cutoff - m.signup_date).dt.days
    out["first_observed_visit"] = c.groupby("member_id").checkin_datetime.min().reindex(out.index)
    out["last_observed_visit"] = c.groupby("member_id").checkin_datetime.max().reindex(out.index)
    out["days_since_last_visit"] = (cutoff - out.last_observed_visit.dt.normalize()).dt.days.astype(float)
    for days in [7, 30, 90]:
        window = c[c.checkin_datetime >= cutoff - pd.Timedelta(days=days)]
        out[f"visits_{days}d"] = window.groupby("member_id").size().reindex(out.index, fill_value=0).astype(float)
        out[f"full_tenure_{days}d"] = out.membership_tenure_days >= days
    previous = c[(c.checkin_datetime >= cutoff - pd.Timedelta(days=60)) &
                 (c.checkin_datetime < cutoff - pd.Timedelta(days=30))]
    out["visits_previous30d"] = previous.groupby("member_id").size().reindex(out.index, fill_value=0).astype(float)
    for days in [30, 90]:
        out[f"attendance_frequency_{days}d"] = out[f"visits_{days}d"] / days * 7
        out.loc[~out[f"full_tenure_{days}d"], f"attendance_frequency_{days}d"] = np.nan
    out["attendance_change_30_vs_previous30"] = out.visits_30d - out.visits_previous30d
    out["attendance_pct_change_30_vs_previous30"] = out.visits_30d / out.visits_previous30d.replace(0, np.nan) - 1
    baseline = (out.visits_90d - out.visits_30d) / 2
    out["attendance_change_30_vs_90_baseline"] = out.visits_30d - baseline
    out.loc[out.membership_tenure_days < 60, ["attendance_change_30_vs_previous30", "attendance_pct_change_30_vs_previous30"]] = np.nan
    out.loc[~out.full_tenure_90d, "attendance_change_30_vs_90_baseline"] = np.nan
    # Eight complete Monday-Sunday weeks; current partial week is excluded.
    week_end = cutoff - pd.Timedelta(days=cutoff.weekday())
    week_start = week_end - pd.Timedelta(weeks=8)
    out["consistency_window_start"] = week_start
    out["consistency_window_end_exclusive"] = week_end
    wc = c[(c.checkin_datetime >= week_start) & (c.checkin_datetime < week_end)].copy()
    wc["week"] = ((wc.checkin_datetime - week_start).dt.days // 7)
    weekly = wc.groupby(["member_id", "week"]).size().unstack(fill_value=0).reindex(index=out.index, columns=range(8), fill_value=0).fillna(0)
    out["active_weeks_8w"] = (weekly > 0).sum(axis=1).astype(float)
    out["attendance_variability"] = weekly.std(axis=1, ddof=0)
    out.loc[m.signup_date > week_start, ["active_weeks_8w", "attendance_variability"]] = np.nan
    recent = c[c.checkin_datetime >= cutoff - pd.Timedelta(days=90)].copy()
    recent["day"] = recent.checkin_datetime.dt.day_name()
    recent["time"] = pd.cut(recent.checkin_datetime.dt.hour, [-1, 4, 11, 16, 21, 23],
                            labels=["overnight_00_05", "morning_05_12", "afternoon_12_17", "evening_17_22", "late_22_24"])
    # Tied modal categories are explicit; deterministic alphabetical listing.
    def mode_label(values):
        counts = values.astype(str).value_counts()
        return "|".join(sorted(counts[counts == counts.max()].index))
    out["preferred_day"] = recent.groupby("member_id").day.agg(mode_label).reindex(out.index)
    out["preferred_time"] = recent.groupby("member_id").time.agg(mode_label).reindex(out.index)
    out["branch_diversity"] = recent.groupby("member_id").location_id.nunique().reindex(out.index, fill_value=0).astype(float)
    out["preference_visit_support_90d"] = out.visits_90d
    numeric_behavior = [col for col in out if col.startswith(("visits_", "attendance_"))] + ["active_weeks_8w", "branch_diversity", "preference_visit_support_90d"]
    out.loc[~observed, numeric_behavior] = np.nan
    return out.reset_index()
