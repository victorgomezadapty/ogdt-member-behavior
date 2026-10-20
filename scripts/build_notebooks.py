"""Create observation notebooks and the explicit per-output feature catalog."""
from pathlib import Path
import csv
import nbformat as nbf

ROOT = Path(__file__).resolve().parents[1]
BOOT = '''from pathlib import Path
import sys
import pandas as pd
from IPython.display import display, Image, Markdown
ROOT = Path.cwd()
if not (ROOT / "src").is_dir():
    ROOT = ROOT.parent
assert (ROOT / "src/data/load.py").exists(), "Run from the repository or notebooks directory"
sys.path.insert(0, str(ROOT))
from src.data.load import load_tables, audit_tables
from src.features.attendance import member_metrics
tables = load_tables(ROOT)
m, c = tables["members"], tables["checkins"]
'''


def notebook(filename, cells):
    nb = nbf.v4.new_notebook(cells=[nbf.v4.new_markdown_cell(body) if kind == "md" else nbf.v4.new_code_cell(body) for kind, body in cells])
    nb.metadata["kernelspec"] = {"display_name": "Python 3", "language": "python", "name": "python3"}
    nb.metadata["ogdt"] = {"milestone": 1, "synthetic": True, "scope": "observation"}
    nbf.write(nb, ROOT / "notebooks" / filename)


def build_catalog():
    rows = []
    caveat = "Synthetic selected sample; capture unverified. No exported visits before cutoff -> null attendance metrics. Counts are not engagement or churn labels."

    def add(name, definition, meaning, window, requirements, limitation, unit):
        rows.append(dict(feature=name, definition=definition, business_meaning=meaning,
                         calculation_window=window, data_requirements=requirements,
                         limitations=limitation, unit=unit, status="implemented_exploratory"))

    for days in [7, 30, 90]:
        add(f"visits_{days}d", f"Count exported events where C-{days} days <= timestamp < C", "Recent attendance volume", f"Trailing {days} calendar days", "member_id; visit_timestamp; explicit C; roster for unknown members", caveat + " Partial tenure counts remain flagged, not extrapolated.", "events")
        add(f"full_tenure_{days}d", f"membership_tenure_days >= {days}", "Window has full signup-based calendar opportunity", f"Signup to C, tested against {days} days", "signup_date; C", "Calendar tenure does not establish complete capture or uninterrupted entitlement.", "boolean")
    for days in [30, 90]:
        add(f"attendance_frequency_{days}d", f"visits_{days}d / {days} * 7; null when tenure < {days}", "Nominal exported attendance per week", f"Trailing {days} days", "member_id; visit_timestamp; signup_date; C", caveat + " Fixed denominator ignores closures/pauses and entitlement.", "events_per_nominal_week")
    add("visits_previous30d", "Count events in [C-60d,C-30d)", "Prior comparison volume", "Previous non-overlapping 30 days", "member_id; visit_timestamp; C", caveat, "events")
    add("attendance_change_30_vs_previous30", "visits_30d - visits_previous30d; null if tenure <60d", "Absolute within-member volume change", "Current 30 vs previous 30 days", "visit_timestamp; member_id; signup_date; C", caveat + " Cancellation/access gaps and sampling may explain change.", "event_difference")
    add("attendance_pct_change_30_vs_previous30", "visits_30d / visits_previous30d - 1; null if previous=0 or tenure<60d", "Relative within-member volume change", "Current 30 vs previous 30 days", "visit_timestamp; member_id; signup_date; C", caveat + " Unstable with small prior count; zero baseline produces null.", "fraction")
    add("attendance_change_30_vs_90_baseline", "visits_30d - (visits_90d-visits_30d)/2; null if tenure<90d", "Current volume against preceding 60-day monthly-equivalent baseline", "Current 30 vs preceding non-overlapping 60 days", "visit_timestamp; member_id; signup_date; C", caveat + " Assumes comparable opportunity; not a decline threshold.", "event_difference")
    add("days_since_last_visit", "Date(C) - date(max exported timestamp < C)", "Calendar recency of last exported attendance", "All exported events strictly before C", "member_id; visit_timestamp; C; source clock", caveat + " Uses calendar-day difference; not elapsed 24-hour periods; final day may be partial.", "days")
    add("membership_tenure_days", "Date(C)-signup_date", "Membership-age context", "Signup to exclusive C", "signup_date; C", "Signup is a proxy; pauses, reactivation and continuous entitlement are unknown. Available even without visits.", "days")
    add("active_weeks_8w", "Number of 8 complete Monday-Sunday weeks with >=1 exported event; null if signup after window start", "Distribution of use across weeks", "[Monday at/before C -56d, Monday at/before C)", "member_id; visit_timestamp; signup_date; C", caveat + " Zero export weeks do not establish verified inactivity or weak habit.", "weeks_0_to_8")
    add("attendance_variability", "Population stddev ddof=0 of 8 complete weekly counts; null if insufficient signup opportunity", "Dispersion of weekly volume", "Same eight complete weeks as active_weeks_8w", "member_id; visit_timestamp; signup_date; C", caveat + " All-zero counts have stddev zero; lower is not necessarily stronger habit.", "events_per_week_stddev")
    add("preferred_day", "Modal day-name(s) among trailing 90d events; ties sorted alphabetically with |", "Observed day concentration", "Trailing 90 days", "member_id; visit_timestamp; C; source clock", caveat + " Unadjusted opportunity; low support and ties explicit; null with no recent visits.", "day_labels")
    add("preferred_time", "Modal source-clock hour band(s): [0,5),[5,12),[12,17),[17,22),[22,24); ties explicit", "Observed clock-window concentration", "Trailing 90 days", "member_id; visit_timestamp; C; source clock", caveat + " Unequal-duration bins and unknown timezone; no opportunity correction; null with no recent visits.", "time_band_labels")
    add("branch_diversity", "Distinct visit location_id count in trailing 90d", "Breadth of recorded branch use", "Trailing 90 days", "member_id; visit_timestamp; event location_id; C", caveat + " Visited branch is not home branch; zero recent records gives zero only in represented cohort.", "branches")
    add("preference_visit_support_90d", "visits_90d", "Evidence supporting modal visit preferences", "Trailing 90 days", "member_id; visit_timestamp; C", caveat + " No fixed support threshold or confidence interval assigned.", "events")
    for name, definition, meaning, unit in [
        ("member_id", "Roster members.id", "Stable output identity", "identifier"),
        ("as_of_exclusive", "Explicit midnight C", "Reproducible snapshot boundary", "datetime"),
        ("synthetic", "True for this source", "Disclose simulated origin", "boolean"),
        ("coverage_verified", "False for every row in public sample", "Expose unmet complete-capture requirement", "boolean"),
        ("sample_observation_status", "visits_present_coverage_unverified if any event before C; otherwise no_visits_in_public_sample", "Distinguish sample absence from attendance states", "categorical"),
        ("first_observed_visit", "Minimum exported visit timestamp before C, else null", "Observed timeline start", "datetime"),
        ("last_observed_visit", "Maximum exported visit timestamp before C, else null", "Observed timeline end", "datetime"),
        ("consistency_window_start", "Monday at/before C minus 56 days", "Audit complete-week window start", "datetime"),
        ("consistency_window_end_exclusive", "Monday at/before C", "Audit complete-week exclusive boundary", "datetime"),
    ]:
        add(name, definition, meaning, "Snapshot at C; first/last use available pre-C history", "Roster; events; explicit C; provenance", "Metadata or timeline boundary, not a behavioral state. Observed boundaries do not establish collection completeness.", unit)
    with (ROOT / "handoff/feature_catalog.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main():
    (ROOT / "notebooks").mkdir(exist_ok=True)
    build_catalog()
    notebook("01_data_understanding.ipynb", [
        ("md", "# 01 · Data understanding\n\n**Synthetic public sample · Milestone 1 observation only.** All substantive public tables are loaded at a pinned revision. Verify schema and coverage before interpreting absence. No ML or churn modeling."),
        ("code", BOOT),
        ("code", 'manifest = (ROOT / "data/raw/manifest.json").read_text()\nprint(manifest)\nfor name, frame in tables.items():\n    print(name, frame.shape)\n    display(pd.DataFrame({"type": frame.dtypes.astype(str), "nulls": frame.isna().sum(), "distinct_nonnull": frame.nunique()}))'),
        ("md", "## Key integrity and event plausibility\n\nHard audit failures block the pipeline. Same-day repeats and overlapping reported durations are retained as flags. Foreign-key joins are validated many-to-one."),
        ("code", 'audit = audit_tables(tables)\ndisplay(pd.Series(audit["checks"], name="failed_record_count").to_frame())\nprint(audit["observations"])\nassert audit["all_hard_checks_pass"]'),
        ("code", 'display(pd.DataFrame({"signup": [m.signup_date.min(), m.signup_date.max()], "checkin": [c.checkin_datetime.min(), c.checkin_datetime.max()], "cancel": [m.cancel_date.min(), m.cancel_date.max()]}, index=["min", "max"]))\nprint("Roster:", len(m), "Observed members:", c.member_id.nunique(), "Unrepresented:", len(m)-c.member_id.nunique())\nprint("Cancel dates:", m.cancel_date.notna().sum(), "Inactive snapshots:", (~m.is_active).sum())\ndisplay(tables["locations"])\ndisplay(tables["plans"])'),
        ("md", "## Interpretation\n\nCancellation dates/reasons and is_active exist publicly, but they are contractual fields, not engagement labels. Event IDs 1–2000 cover member IDs 1–32; absence for 268 members is not inactivity. No public class-booking or operational anomaly event table exists. Closure and promotion are described without dates/branches or ground truth. See docs/data_dictionary.md, docs/entity_relationships.md and docs/dataset_limitations.md."),
    ])
    notebook("02_member_attendance_eda.ipynb", [
        ("md", "# 02 · Member attendance EDA\n\n**Synthetic selected public sample.** Descriptive volume, intervals, early attendance and context. The 32-member attendance cohort is selected from the export, not a representative population. Run scripts/analyze.py first."),
        ("code", BOOT),
        ("code", 'counts = c.groupby("member_id").size()\ndisplay(counts.describe().to_frame("exported_events"))\nfor name in ["member_week", "member_month"]:\n    panel = pd.read_csv(ROOT / f"data/processed/{name}.csv")\n    print(name, "rows", len(panel), "zero-export share", panel.exported_events.eq(0).mean())\n    display(panel.head())'),
        ("code", 'for name in ["branch_summary", "plan_summary", "tenure_summary"]:\n    print(name)\n    display(pd.read_csv(ROOT / f"data/processed/{name}.csv"))\ngaps = c.sort_values("checkin_datetime").groupby("member_id").checkin_datetime.diff().dt.total_seconds()/86400\ndisplay(gaps.describe().to_frame("days_between_exported_events"))'),
        ("code", 'for name in ["01_coverage_and_volume", "03_week_month_distributions", "06_membership_tenure", "07_branch_and_plan", "11_early_behavior_and_gaps"]:\n    display(Image(filename=str(ROOT / f"reports/figures/{name}.png")))'),
        ("md", "## Interpretation\n\nVolume distributions include zero exported records after signup, including calendar time after available cancellation dates. Partial calendar periods are flagged. Neither those periods nor signup-derived opportunity establish entitlement or complete capture. Unequal tenure/follow-up and subgroup support prevent engagement rankings. Session gaps include same-day repeats and sampling uncertainty. Do not establish state thresholds from these descriptive bins."),
    ])
    notebook("03_temporal_behavior.ipynb", [
        ("md", "# 03 · Temporal observation and candidate metrics\n\n**Synthetic public sample · no states, segmentation or risk scoring.** Inspect day/hour/month patterns and individual histories; candidate metrics use a dataset-relative exclusive cutoff and disclose unverified capture."),
        ("code", BOOT),
        ("code", 'for name in ["day_summary", "hour_summary", "monthly_summary"]:\n    print(name)\n    display(pd.read_csv(ROOT / f"data/processed/{name}.csv"))'),
        ("code", 'for name in ["02_visit_timeline", "04_day_preference", "05_time_preference", "08_monthly_patterns", "09_member_month_heatmap", "10_individual_trajectories"]:\n    display(Image(filename=str(ROOT / f"reports/figures/{name}.png")))'),
        ("code", 'cutoff = c.checkin_datetime.max().normalize() + pd.Timedelta(days=1)\nfeatures = member_metrics(m, c, cutoff)\nprint("Exclusive cutoff", cutoff, "timezone unspecified")\ndisplay(features.head())\ndisplay(features.sample_observation_status.value_counts().to_frame())\nunknown = features.sample_observation_status.eq("no_visits_in_public_sample")\nassert features.loc[unknown, "visits_30d"].isna().all()\nassert not features.coverage_verified.any()\ndisplay(pd.read_csv(ROOT / "handoff/feature_catalog.csv"))'),
        ("md", "## Proposed Phase 2\n\nVerify event capture, timezone, entitlement and operating calendars. Examine recency, frequency, trend and consistency jointly with tenure; compare within-member trajectories; calibrate candidate rules against distributions and operational review before state definitions. Synthetic monthly curves cannot prove January/summer or closure/promotion effects. Behavioral risk would not be contractual churn probability. Secondary datasets must test methods independently, never row-merge members."),
    ])
    for filename, title in [("04_member_states.ipynb", "Member states"), ("05_segmentation.ipynb", "Segmentation"), ("06_behavioral_risk.ipynb", "Behavioral risk")]:
        notebook(filename, [("md", f"# {title} — deferred\n\n**Intentionally not implemented in Milestone 1.**\n\nFirst establish member-level event capture and temporal/exposure validity, inspect distributions, and validate operational interpretations. No final thresholds, states, clusters or risk scores exist. Behavioral risk must remain separate from contractual churn probability. See docs/behavioral_state_definition.md and handoff/module_spec.md for Phase 2 gates.")])
    print("Built three observation notebooks, three deferred outlines, and feature catalog")


if __name__ == "__main__":
    main()
