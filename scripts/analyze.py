"""Rebuild Milestone 1 audit, descriptive exports, figures and report offline."""
from pathlib import Path
import sys
import json
import html
import platform
import importlib.metadata
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.data.load import load_tables, audit_tables
from src.features.attendance import member_metrics
from src.visualization.plots import create_figures


def markdown_table(frame):
    frame = frame.astype(object).where(frame.notna(), "—")
    escape = lambda x: str(x).replace("|", "\\|").replace("\n", " ")
    return "| " + " | ".join(map(escape, frame.columns)) + " |\n| " + " | ".join(["---"] * len(frame.columns)) + " |\n" + "\n".join("| " + " | ".join(map(escape, row)) + " |" for row in frame.itertuples(index=False, name=None))


def make_panels(members, checkins):
    start = checkins.checkin_datetime.min().normalize()
    end = checkins.checkin_datetime.max().normalize()
    subset = members[members.id.isin(checkins.member_id.unique())]
    panels = []
    for frequency in ["M", "W-SUN"]:
        periods = pd.period_range(start, end, freq=frequency)
        counts = checkins.groupby(["member_id", checkins.checkin_datetime.dt.to_period(frequency)]).size()
        rows = []
        for member in subset.itertuples(index=False):
            for period in periods:
                first = max(period.start_time, start, member.signup_date)
                last = min(period.end_time.normalize(), end)
                if first <= last:
                    rows.append({"member_id": member.id, "period": str(period),
                                 "exported_events": int(counts.get((member.id, period), 0)),
                                 "calendar_opportunity_days": (last-first).days+1,
                                 "boundary_or_signup_partial": first != period.start_time or last != period.end_time.normalize(),
                                 "coverage_verified": False})
        panels.append(pd.DataFrame(rows))
    return panels


def main():
    for directory in ["data/processed", "reports/figures", "docs", "handoff"]:
        (ROOT / directory).mkdir(parents=True, exist_ok=True)
    tables = load_tables()
    audit = audit_tables(tables)
    (ROOT / "reports/data_quality.json").write_text(json.dumps(audit, indent=2, default=int) + "\n", encoding="utf-8")
    if not audit["all_hard_checks_pass"]:
        raise ValueError("Resolve hard audit failures before analysis; see reports/data_quality.json")
    m, c = tables["members"], tables["checkins"]
    start, end = c.checkin_datetime.min().normalize(), c.checkin_datetime.max().normalize()
    cutoff = end + pd.Timedelta(days=1)
    metrics = member_metrics(m, c, cutoff)
    metrics.to_csv(ROOT / "data/processed/member_metrics.csv", index=False)
    joined = c.merge(m[["id", "signup_date", "plan_id", "location_id"]].rename(columns={"id": "member_id", "location_id": "home_location_id"}), on="member_id", validate="many_to_one")
    joined = joined.merge(tables["plans"][["id", "name"]].rename(columns={"id": "plan_id", "name": "plan_name"}), on="plan_id", validate="many_to_one")
    joined = joined.merge(tables["locations"][["id", "name"]].rename(columns={"id": "location_id", "name": "visit_branch"}), on="location_id", validate="many_to_one")
    joined["tenure_days"] = (joined.checkin_datetime.dt.normalize() - joined.signup_date).dt.days
    joined["tenure_band"] = pd.cut(joined.tenure_days, [-1, 29, 89, 179, 364, float("inf")], labels=["0–29", "30–89", "90–179", "180–364", "365+"])
    joined["time_band"] = pd.cut(joined.checkin_datetime.dt.hour, [-1, 4, 11, 16, 21, 23], labels=["00–04", "05–11", "12–16", "17–21", "22–23"])
    joined.to_csv(ROOT / "data/processed/visits_enriched.csv", index=False)
    member_month, weekly = make_panels(m, c)
    member_month = member_month.rename(columns={"period": "month"})
    weekly = weekly.rename(columns={"period": "week"})
    member_month.to_csv(ROOT / "data/processed/member_month.csv", index=False)
    weekly.to_csv(ROOT / "data/processed/member_week.csv", index=False)
    monthly = pd.DataFrame({"month": pd.period_range(start, end, freq="M").astype(str)})
    monthly["exported_events"] = monthly.month.map(c.groupby(c.checkin_datetime.dt.to_period("M").astype(str)).size()).fillna(0).astype(int)
    monthly["members_with_exported_events"] = monthly.month.map(c.groupby(c.checkin_datetime.dt.to_period("M").astype(str)).member_id.nunique()).fillna(0).astype(int)
    monthly["roster_signups"] = monthly.month.map(m.groupby(m.signup_date.dt.to_period("M").astype(str)).size()).fillna(0).astype(int)
    monthly["selected_member_calendar_days"] = monthly.month.map(member_month.groupby("month").calendar_opportunity_days.sum())
    monthly["events_per_selected_member_calendar_day"] = monthly.exported_events / monthly.selected_member_calendar_days
    monthly["boundary_month"] = monthly.month.isin([str(start.to_period("M")), str(end.to_period("M"))])
    monthly.to_csv(ROOT / "data/processed/monthly_summary.csv", index=False)
    monthly.attrs["member_panel"] = member_month
    branch = joined.groupby("visit_branch").agg(events=("id", "size"), members_with_events=("member_id", "nunique")).reset_index()
    plan = joined.groupby("plan_name").agg(events=("id", "size"), members_with_events=("member_id", "nunique")).reset_index()
    tenure = joined.groupby("tenure_band", observed=False).agg(events=("id", "size"), members_with_events=("member_id", "nunique")).reset_index()
    for name, frame in [("branch_summary", branch), ("plan_summary", plan), ("tenure_summary", tenure)]:
        frame.to_csv(ROOT / f"data/processed/{name}.csv", index=False)
    daily = c.groupby(c.checkin_datetime.dt.dayofweek).size().reindex(range(7), fill_value=0)
    day_frame = pd.DataFrame({"day": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"], "events": daily.values})
    calendar_counts = pd.Series(pd.date_range(start, end).dayofweek).value_counts().reindex(range(7))
    day_frame["observed_calendar_days"] = calendar_counts.values
    day_frame["events_per_calendar_day"] = (daily / calendar_counts).values
    day_frame.to_csv(ROOT / "data/processed/day_summary.csv", index=False)
    hour_frame = c.groupby(c.checkin_datetime.dt.hour).size().reindex(range(24), fill_value=0).rename("events").rename_axis("clock_hour").reset_index()
    hour_frame.to_csv(ROOT / "data/processed/hour_summary.csv", index=False)
    timeline = []
    for member in m.itertuples(index=False):
        timeline.append({"member_id": member.id, "event_type": "signup", "timestamp": member.signup_date})
        for label, date in [("first_exported_visit", c.loc[c.member_id == member.id, "checkin_datetime"].min()),
                            ("last_exported_visit", c.loc[c.member_id == member.id, "checkin_datetime"].max()),
                            ("recorded_cancel_date", member.cancel_date)]:
            if pd.notna(date):
                timeline.append({"member_id": member.id, "event_type": label, "timestamp": date})
    pd.DataFrame(timeline).sort_values(["member_id", "timestamp", "event_type"]).to_csv(ROOT / "data/processed/member_timeline.csv", index=False)
    figures = create_figures(tables, joined, monthly, weekly, ROOT / "reports/figures")
    descriptions = {
        "members": {"id": "Member identifier; candidate primary key.", "first_name": "Synthetic given name; excluded from analytics.", "last_name": "Synthetic family name; excluded from analytics.", "email": "Synthetic contact address; unnecessary for behavior metrics.", "phone": "Synthetic phone; unnecessary for behavior metrics.", "signup_date": "Date-only signup; proxy membership start, not first visit.", "plan_id": "Current/static plan reference; no plan history.", "location_id": "Home branch reference; may differ from visit branch.", "is_active": "Undated contract status snapshot; not attendance engagement.", "cancel_date": "Nullable date-only contractual cancellation field.", "cancel_reason": "Nullable synthetic cancellation reason; no outcome modeling here."},
        "checkins": {"id": "Visit identifier; candidate primary key.", "member_id": "Member reference.", "location_id": "Visited branch reference.", "checkin_datetime": "Naive timestamp; source timezone and acquisition completeness unknown.", "duration_minutes": "Reported session duration in minutes; not measured exercise quality."},
        "locations": {"id": "Branch identifier; primary key.", "name": "Synthetic branch label.", "capacity": "Reported capacity; unit/occupancy interpretation undocumented.", "has_pool": "Boolean pool availability."},
        "plans": {"id": "Plan identifier; primary key.", "name": "Plan label; includes annual, monthly, student.", "price": "Price; currency and billing semantics not fully documented.", "share": "Reported plan-share parameter; not measured member proportion."}}
    dictionary = "# Data dictionary\n\nSynthetic public sample; generated from all four downloaded tables. Counts reflect the pinned revision. See `data/raw/manifest.json` for source hashes.\n\n"
    for name, frame in tables.items():
        rows = []
        for col in frame:
            series = frame[col]
            if col in ["first_name", "last_name", "email", "phone"]:
                example = "[contact field omitted]"
            elif pd.api.types.is_datetime64_any_dtype(series):
                example = f"{series.min()} → {series.max()}"
            elif pd.api.types.is_numeric_dtype(series) and not pd.api.types.is_bool_dtype(series):
                example = f"{series.min()} → {series.max()}"
            else:
                example = ", ".join(map(str, series.dropna().unique()[:5]))
            rows.append({"Field": col, "Parsed type": str(series.dtype), "Nulls": int(series.isna().sum()), "Distinct non-null": int(series.nunique()), "Observed range / examples": example, "Meaning / caveat": descriptions[name][col]})
        dictionary += f"## {name} ({len(frame):,} rows)\n\n" + markdown_table(pd.DataFrame(rows)) + "\n\n"
    dictionary += "Missing cancellation fields coincide with the 160 active-status rows in this revision. This is structural missingness; it does not establish future retention. Dates carry no timezone; cancellation dates lack within-day ordering. Plan shares sum to " + f"{tables['plans'].share.sum():.2f}.\n"
    (ROOT / "docs/data_dictionary.md").write_text(dictionary, encoding="utf-8")
    count_stats = c.groupby("member_id").size().describe()
    gaps = c.sort_values("checkin_datetime").groupby("member_id").checkin_datetime.diff().dt.total_seconds().div(86400).dropna()
    early_members = m[m.id.isin(c.member_id) & (m.signup_date >= start) & (m.signup_date + pd.Timedelta(days=30) <= cutoff)]
    early_counts = joined[joined.tenure_days < 30].groupby("member_id").size().reindex(early_members.id, fill_value=0)
    quality_table = pd.DataFrame([{"Check": k, "Count": v} for k, v in audit["checks"].items()])
    observations = audit["observations"]
    report = f"""# Milestone 1 — Observe Member Behavior

**Gym Member Behavior & Engagement Intelligence · Open Gym Digital Twin**

**All data and results are synthetic. This is a selected public sample, not a real-gym study.**
Source: [Mindweave / Hugging Face](https://huggingface.co/datasets/mindweave/gym-memberships), revision `{json.loads((ROOT/'data/raw/manifest.json').read_text())['revision']}`. Analysis date: 2026-10-13. Data clock: 2023–2024; recency uses the dataset cutoff, never today's date.

## The central result is a coverage constraint

There are **{len(m)} roster members**, **{len(c):,} exported check-ins**, **3 branches**, and **5 plans**. Visits cover **{c.member_id.nunique()} members ({c.member_id.nunique()/len(m):.1%})**, IDs {c.member_id.min()}–{c.member_id.max()}. The other **{len(m)-c.member_id.nunique()} members have no check-ins in the export**. Event IDs are {c.id.min()}–{c.id.max()}, consecutive in this revision. This ordering is consistent with a member-ordered excerpt; the provider does not document its sampling mechanism or complete capture. Even ID 32's completeness is unknown. Missing exported records cannot establish inactivity, disengagement, or churn.

## Architecture and time bounds

Four CSV tables loaded and checked: members → plans/home locations; check-ins → members/visited locations. See [entity relationships](../docs/entity_relationships.md) and [dictionary](../docs/data_dictionary.md).

- Signup dates: {m.signup_date.min().date()} to {m.signup_date.max().date()}.
- Check-ins: {c.checkin_datetime.min()} to {c.checkin_datetime.max()}.
- Non-null cancellation dates: {m.cancel_date.min().date()} to {m.cancel_date.max().date()}.
- Exclusive feature cutoff: **{cutoff}**, timezone unspecified. The last recorded day may be incomplete.
- Public cancellation data is present: **{m.cancel_date.notna().sum()} cancel dates**, **{m.cancel_reason.notna().sum()} reasons**, **{(~m.is_active).sum()} inactive-status rows**. These are contractual snapshot fields. They do not define attendance states and are excluded from feature calculations.
- No class bookings, renewal, expiration, operational closure calendar, anomaly labels, plan history, or per-member extraction completeness fields exist in the public tables.

## Quality audit

All {len(audit['checks'])} hard integrity checks pass at the pinned revision. No records are silently deleted. Null counts are in the dictionary and `reports/data_quality.json`.

{markdown_table(quality_table)}

Additional observations, retained for review: **{observations['multi_visit_member_days']} member-days with multiple visits**, **{observations['overlapping_sessions']} overlapping reported sessions**, **{observations['checkins_on_cancel_day']} visits on cancellation dates**, **{observations['visits_away_from_home_branch']} visits away from the home branch**. Multiple events per day are not deduplicated merely for sharing a day. Overlaps are a plausibility flag; assess real access-log semantics before deployment. Duration spans {c.duration_minutes.min()}–{c.duration_minutes.max()} minutes; no undocumented upper threshold is treated as an error.

## Attendance distributions and intervals

Among the 32 members with exported visits, total-event count median is **{count_stats['50%']:.1f}**, IQR **{count_stats['25%']:.1f}–{count_stats['75%']:.1f}**, range **{int(count_stats['min'])}–{int(count_stats['max'])}**, mean **{count_stats['mean']:.2f}**. Totals span different tenure and follow-up windows; they are not comparable engagement labels.

The selected-member calendar panels contain **{len(weekly)} member-weeks** and **{len(member_month)} member-months** after signup within the observed export span. Median exported counts are **{weekly.exported_events.median():.1f}/week** and **{member_month.exported_events.median():.1f}/month**; zero-export shares are **{weekly.exported_events.eq(0).mean():.1%}** and **{member_month.exported_events.eq(0).mean():.1%}**. Boundary/signup partial periods are flagged. Periods after a recorded cancellation are retained as calendar context, not counted as entitlement or inactivity evidence.

Median gap between consecutive exported events is **{gaps.median():.2f} days** (IQR {gaps.quantile(.25):.2f}–{gaps.quantile(.75):.2f}; {len(gaps)} intervals). Gaps can reflect sampling and include same-day repeats.

## Day and time

{markdown_table(day_frame.round(3))}

Peak recorded clock hour is **{int(hour_frame.loc[hour_frame.events.idxmax(), 'clock_hour']):02d}:00**. All 24 hourly counts are exported. Time bins are display conventions, not behavioral thresholds; unequal bin durations preclude a simple preference comparison without hour adjustment. Weekend figures use Saturday/Sunday for exploratory display only, not a jurisdiction-specific operational calendar.

## Tenure, early behavior, plans, and branches

Tenure is calendar days from signup to event, not continuous active membership duration. Tenure bands are descriptive bins, not engagement rules; follow-up and population exposure are unequal.

{markdown_table(tenure)}

First-30-tenure-day distribution: **{len(early_members)} selected members** have 30 calendar days of opportunity within the export span; median exported count **{early_counts.median():.1f}**, range **{early_counts.min()}–{early_counts.max()}**. Calendar opportunity does not verify full event capture or membership entitlement.

{markdown_table(branch)}

{markdown_table(plan)}

Plan is a static snapshot and cannot establish the plan held at each historical visit. Raw subgroup counts reflect unequal sample support. Branch differences cannot establish comparative performance.

## Monthly patterns

{markdown_table(monthly.round(4))}

The exported visit peak is **{monthly.loc[monthly.exported_events.idxmax(), 'month']} ({monthly.exported_events.max()} events)**. The roster contains **{m.signup_date.dt.month.eq(1).sum()} January signups** across two years. Compare same months across years in Figure 08. The adjusted export-density denominator counts selected members' calendar days since signup inside the observed span; it ignores contract entitlement and is not an attendance rate. The selected population changes with signup, and export completeness is unknown. Do not infer a validated January effect, summer effect, closure, or promotional impact from these totals. Only two synthetic years and no anomaly event dates/branches are available.

## Individual trajectories and member timeline

Figure 09 shows every member with exported visits. Figure 10 selects six members deterministically at evenly spaced attendance-volume ranks, showing signup and available cancellation-date overlays. This exposes trajectory heterogeneity without assigning states. `member_timeline.csv` includes signup, first/last exported visit, and recorded cancellation where available for all roster members. Habit formation, stable attendance, decline, and inactivity are not asserted as timeline events without validated definitions.

## Candidate metrics and real-gym requirements

`member_metrics.csv` contains 300 rows at the dataset cutoff. Members without exported events retain null attendance metrics and `no_visits_in_public_sample`. The 32 other rows have sample-derived candidates, all with `coverage_verified=false`. Recent zero counts in those rows still mean zero exported records, not verified inactivity. Every feature is defined with window, meaning, requirements, and limits in [feature catalog](../handoff/feature_catalog.csv) and [metric definitions](../handoff/metrics_definition.md).

Minimum real-gym inputs: stable member ID and visit timestamp, plus extraction coverage and timezone metadata to interpret absence. Add membership start for tenure, event branch and plan history for context, and closure calendars for exposure. Contractual outcomes belong to the Retention Module. See [data contract](../handoff/data_contract.yaml).

## Limits and proposed Phase 2

Synthetic generation, selected member/event export, undated status snapshots, unspecified timezone, no entitlement/history or acquisition coverage, and unlabelled operational anomalies prevent real-world engagement or churn claims. See [dataset limitations](../docs/dataset_limitations.md).

Phase 2: obtain a dataset with verified member-level event coverage; audit windows and closures; examine recency, frequency, trend and consistency jointly with tenure-aware denominators; compare same-member trajectories; calibrate candidate thresholds against distributions and operational review; assess temporal stability before state definitions. Only then consider interpretable segmentation tied to specific decisions. A later secondary dataset should test methods independently, never row-merge unrelated people. Behavioral risk is not churn probability. No ML, final states, clusters, risk scores, or churn model were produced in Milestone 1.

## Figures

"""
    for name, title in figures:
        report += f"### {title}\n\n![{title}](figures/{name}.png)\n\n"
    (ROOT / "reports/milestone_1.md").write_text(report, encoding="utf-8")
    findings = f"""# Findings — Milestone 1

Synthetic public sample only. These are observations and reusable methodological lessons, not population estimates.

- {len(m)} roster members, {len(c):,} visits, {c.member_id.nunique()} members with exported visits; {len(m)-c.member_id.nunique()} have unknown attendance coverage.
- Cancel dates/reasons and is_active are public. {m.cancel_date.notna().sum()} rows have cancellation dates. Contract fields must remain conceptually separate from attendance features.
- The selected cohort's median lifetime exported events is {count_stats['50%']:.1f}; median inter-event gap is {gaps.median():.2f} days. These values are not state thresholds.
- {observations['overlapping_sessions']} session overlaps warrant investigation of event semantics; no rows were automatically dropped.
- Audit primary/foreign keys and sampling before modeling. A roster left join must distinguish no exported records from observed inactivity.
- Compare volume, recency, trend, consistency and tenure jointly; calendar boundaries, member entry and incomplete exposure change interpretation.
- Static plan/status values cannot be used as historical facts without effective dates. Source-clock timestamps need timezone metadata.
- Complete logs and operational context are prerequisites for actionable states. Synthetic seasonality or anomalies cannot establish real-gym causal effects.

All numerical results and figures: [Milestone 1 report](../reports/milestone_1.md). Definitions: [metric catalog](feature_catalog.csv). Phase 2 is proposed, not implemented.
"""
    (ROOT / "handoff/findings.md").write_text(findings, encoding="utf-8")
    versions = {"python": platform.python_version()}
    for package in ["numpy", "pandas", "matplotlib", "nbformat", "nbclient", "ipykernel", "PyYAML"]:
        try:
            versions[package] = importlib.metadata.version(package)
        except importlib.metadata.PackageNotFoundError:
            versions[package] = "not installed"
    (ROOT / "reports/environment.json").write_text(json.dumps(versions, indent=2) + "\n", encoding="utf-8")
    summary = {"synthetic": True, "scope": "public sample", "members": len(m), "checkins": len(c), "members_with_visits": c.member_id.nunique(), "cancel_dates": int(m.cancel_date.notna().sum()), "feature_cutoff_exclusive": str(cutoff), "figures": len(figures), "hard_checks_pass": audit["all_hard_checks_pass"]}
    (ROOT / "reports/summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    # Self-contained local report; figures embedded so copying HTML preserves visuals.
    import base64
    gallery = "".join(f'<section><h2>{html.escape(title)}</h2><img alt="{html.escape(title)}" src="data:image/png;base64,{base64.b64encode((ROOT / f"reports/figures/{name}.png").read_bytes()).decode()}"></section>' for name, title in figures)
    page = f'''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>OGDT · Observe Member Behavior</title><style>body{{font:16px/1.65 system-ui;background:#f1f4f7;color:#172a3a;margin:0}}main{{max-width:1100px;margin:auto;padding:40px 24px}}h1{{font-size:clamp(32px,5vw,50px);line-height:1.15}}.eyebrow{{color:#235789;letter-spacing:2px;font-weight:700}}.warning{{background:#fff1d8;border-left:5px solid #d06b2d;padding:20px}}.cards{{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin:24px 0}}.card,section{{background:white;padding:20px;border-radius:10px}}.card strong{{font-size:32px;display:block}}section{{margin:20px 0}}img{{width:100%;height:auto}}a{{color:#235789}}pre{{white-space:pre-wrap;font:14px/1.65 system-ui}}@media(max-width:600px){{.cards{{grid-template-columns:1fr 1fr}}}}</style><main><p class="eyebrow">OPEN GYM DIGITAL TWIN / MEMBER BEHAVIOR LAB</p><h1>Observe member behavior.<br>Understand the limits first.</h1><p>Gym Member Behavior &amp; Engagement Intelligence · Milestone 1 · 13 October 2026</p><div class="warning"><strong>Synthetic public sample — attendance coverage is unverified.</strong><br>268 roster members have no exported visits. That absence cannot establish inactivity, disengagement or churn. Candidate metrics are exploratory; no ML or state thresholds.</div><div class="cards"><div class="card"><strong>300</strong>Roster members</div><div class="card"><strong>2,000</strong>Exported visits</div><div class="card"><strong>32</strong>Members with visits</div><div class="card"><strong>140</strong>Recorded cancel dates</div></div><p>Observation clock: 12 January 2023–28 December 2024. Recency cutoff: 29 December 2024, exclusive; timezone unknown. Cancellation fields are available and remain separate from attendance metrics.</p><p><a href="milestone_1.md">Full report</a> · <a href="../docs/data_dictionary.md">Data dictionary</a> · <a href="../docs/entity_relationships.md">Architecture</a> · <a href="../handoff/feature_catalog.csv">Feature catalog</a> · <a href="../docs/dataset_limitations.md">Limitations</a></p>{gallery}<section><h2>Complete analytical narrative and tables</h2><pre>{html.escape(report.split('## Figures')[0])}</pre></section><p>Source: <a href="https://huggingface.co/datasets/mindweave/gym-memberships">Mindweave / Hugging Face</a> · CC-BY-NC-4.0 · All findings concern a synthetic excerpt.</p></main></html>'''
    (ROOT / "reports/milestone_1.html").write_text(page, encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
