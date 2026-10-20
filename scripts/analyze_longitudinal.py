"""Build a descriptive extension of Observe without assigning engagement states."""
from pathlib import Path
import sys
import json
import html
import base64
import importlib.metadata
import platform
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm
import nbformat as nbf

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.data.load import load_tables, audit_tables
from src.features.longitudinal import observation_cutoffs, longitudinal_metrics, feature_diagnostics, summarize_snapshots, window_sensitivity, eligible_rows


def md_table(frame):
    def escape(value):
        return str(value).replace("|", "\\|")
    f = frame.astype(object).where(frame.notna(), "—")
    return "| " + " | ".join(f.columns) + " |\n| " + " | ".join(["---"]*len(f.columns)) + " |\n" + "\n".join("| " + " | ".join(map(escape, row)) + " |" for row in f.itertuples(index=False, name=None))


def build_figures(panel, summary, final, sensitivity, diagnostics, target):
    target.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10, "axes.spines.top": False, "axes.spines.right": False})
    figures = []
    blue, teal, orange = "#235789", "#16817a", "#d06b2d"

    def save(fig, name, title):
        fig.suptitle(title, x=.06, y=.98, ha="left", fontsize=16, fontweight="bold")
        fig.text(.06, .91, "SYNTHETIC SELECTED SAMPLE · All attendance capture remains unverified", color="#626b73", fontsize=9)
        fig.text(.06, .025, "Exploratory exported-event metrics. Signs and zero counts are not engagement states or churn probabilities.", color="#626b73", fontsize=9)
        fig.tight_layout(rect=(.02, .06, .98, .86))
        fig.savefig(target / f"{name}.png", dpi=150)
        plt.close(fig)
        figures.append((name, title))

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    axes[0].plot(summary.as_of_exclusive, summary.signed_up_roster, label="Exported roster signed up before cutoff", color=blue)
    axes[0].plot(summary.as_of_exclusive, summary.members_with_exported_history, label="Exported visit history before cutoff", color=teal)
    axes[0].set_ylabel("Members")
    axes[0].legend(fontsize=8)
    for days, color in [(30, blue), (60, teal), (90, orange)]:
        axes[1].plot(summary.as_of_exclusive, summary[f"calendar_eligible_{days}d"], label=f"{days}-day calendar opportunity", color=color)
    axes[1].set_ylabel("Represented members; capture still unverified")
    axes[1].legend(fontsize=8)
    for ax in axes:
        ax.tick_params(axis="x", rotation=35)
    save(fig, "01_snapshot_support", "Historical support grows with signup and exported history")

    display_panel = panel.copy()
    display_panel.loc[~eligible_rows(display_panel, 60), "attendance_change_30_vs_previous30"] = np.nan
    matrix = display_panel.pivot(index="member_id", columns="as_of_exclusive", values="attendance_change_30_vs_previous30").dropna(how="all")
    fig, ax = plt.subplots(figsize=(12, 8))
    cmap = plt.get_cmap("PuOr").copy()
    cmap.set_bad("#e4e7eb")
    bound = max(1, np.nanmax(np.abs(matrix.to_numpy())))
    im = ax.imshow(matrix.to_numpy(), aspect="auto", cmap=cmap, norm=TwoSlopeNorm(vmin=-bound, vcenter=0, vmax=bound))
    ax.set_yticks(range(len(matrix)), matrix.index)
    ax.set_xticks(range(len(matrix.columns)), [pd.Timestamp(d).strftime("%Y-%m-%d") for d in matrix.columns], rotation=65, ha="right")
    ax.set_ylabel("Member ID; gray = no eligible export-based comparison")
    fig.colorbar(im, ax=ax, label="Current 30-day exported events − previous 30 days")
    save(fig, "02_member_change_panel", "Within-member count changes vary across historical cutoffs")

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    f = final.loc[eligible_rows(final, 60)]
    axes[0].scatter(f.days_since_last_visit, f.visits_30d, color=blue, edgecolors="white", s=70)
    axes[0].set_xscale("symlog", linthresh=7)
    axes[0].set_xlabel("Calendar days since last exported visit (symlog)")
    axes[0].set_ylabel("Exported events in last 30 days")
    available = final.active_weeks_8w.notna() & final.consistency_inside_export_span
    points = axes[1].scatter(final.loc[available, "active_weeks_8w"], final.loc[available, "attendance_variability"], c=final.loc[available, "visits_30d"], cmap="viridis", s=70, edgecolors="white")
    axes[1].set_xlabel("Complete weeks with exported events (out of 8)")
    axes[1].set_ylabel("Weekly count population standard deviation")
    axes[1].set_xticks(range(9))
    fig.colorbar(points, ax=axes[1], label="Exported visits, last 30 days")
    axes[0].set_title(f"Recency / volume; n={len(f)}", fontsize=11)
    axes[1].set_title(f"Consistency / variability; n={int(available.sum())}", fontsize=11)
    save(fig, "03_joint_metrics", "Joint metrics expose why one attendance count is insufficient")

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    x, y = sensitivity.attendance_change_30_vs_previous30, sensitivity.attendance_change_30_vs_90_baseline
    axes[0].scatter(x, y, color=blue, alpha=.75, s=65, edgecolors="white")
    for value in [0]:
        axes[0].axhline(value, color="#999", lw=.7)
        axes[0].axvline(value, color="#999", lw=.7)
    axes[0].set_xlabel("Change vs previous 30 days (events)")
    axes[0].set_ylabel("Change vs prior 60-day monthly baseline")
    axes[0].set_title(f"Identical 90-day calendar-eligible cohort, n={len(sensitivity)}", fontsize=10)
    axes[1].scatter(sensitivity.attendance_frequency_90d, sensitivity.attendance_frequency_30d, color=teal, s=65, alpha=.75, edgecolors="white")
    top = max(sensitivity.attendance_frequency_90d.max(), sensitivity.attendance_frequency_30d.max(), 1)
    axes[1].plot([0, top], [0, top], color="#999", ls="--", label="Equal nominal frequency")
    axes[1].set_xlabel("90-day exported events / nominal week")
    axes[1].set_ylabel("30-day exported events / nominal week")
    axes[1].legend(fontsize=8)
    save(fig, "04_window_sensitivity", "Baseline and window choices change the descriptive signal")

    fig, axes = plt.subplots(1, 2, figsize=(12, 6))
    labels = diagnostics.feature.str.replace("attendance_", "", regex=False)
    axes[0].barh(labels, diagnostics.non_null_roster, color=blue)
    axes[0].set_xlim(0, len(final))
    axes[0].set_xlabel(f"Non-null values in {len(final)} roster rows")
    axes[1].barh(labels, diagnostics.distinct_values_represented, color=teal)
    axes[1].set_xlabel("Distinct values among represented non-null rows")
    save(fig, "05_feature_support", "Feature availability and variation limit interpretation")
    return figures


def main():
    out, reports = ROOT / "data/processed/longitudinal", ROOT / "reports/longitudinal"
    out.mkdir(parents=True, exist_ok=True)
    reports.mkdir(parents=True, exist_ok=True)
    tables = load_tables()
    if not audit_tables(tables)["all_hard_checks_pass"]:
        raise ValueError("Source audit must pass before longitudinal exploration")
    m, c = tables["members"], tables["checkins"]
    cutoffs = observation_cutoffs(c)
    panel = longitudinal_metrics(m, c, cutoffs)
    summary = summarize_snapshots(panel)
    final = panel[panel.as_of_exclusive.eq(cutoffs[-1])].copy()
    diagnostics = feature_diagnostics(final)
    sensitivity = window_sensitivity(final)
    for name, frame in [("member_snapshots", panel), ("snapshot_summary", summary), ("feature_diagnostics", diagnostics), ("window_sensitivity", sensitivity)]:
        frame.to_csv(out / f"{name}.csv", index=False)
    figures = build_figures(panel, summary, final, sensitivity, diagnostics, reports / "figures")
    final_summary = summary.iloc[-1]
    sign_mismatches = int((~sensitivity.baseline_change_sign_agrees).sum())
    # Same current exported count, different changes; deterministic pair selection.
    valid = final.loc[eligible_rows(final, 60)].sort_values("member_id")
    examples = []
    for volume, group in valid.groupby("visits_30d"):
        if volume > 0 and group.attendance_change_30_vs_previous30.nunique() > 1:
            pair = group.sort_values(["attendance_change_30_vs_previous30", "member_id"]).iloc[[0, -1]]
            examples = pair[["member_id", "visits_30d", "visits_previous30d", "attendance_change_30_vs_previous30"]].to_dict("records")
            break
    example_frame = pd.DataFrame(examples)
    example_frame.to_csv(out / "same_volume_different_history.csv", index=False)
    readiness = {
        "synthetic": True, "status": "exploratory_only", "assessed_at": "2026-10-18",
        "operational_states_ready": False, "threshold_calibration_ready": False,
        "unmet_requirements": [
            {"requirement": "member_event_capture_windows", "evidence": "No per-member acquisition window, gaps or complete-capture assertion in public files", "needed": "Member-specific verified capture intervals and extraction bounds"},
            {"requirement": "timestamp_timezone", "evidence": "Naive check-in timestamps; no source timezone metadata", "needed": "Documented IANA zone or explicit offsets and DST interpretation"},
            {"requirement": "effective_access_and_operating_context", "evidence": "Signup/current plan/cancel snapshot only; no pauses, access ledger, opening hours or closure calendar", "needed": "Effective access intervals, pauses and operational calendars"}],
        "allowed_output": "Descriptive exported-event summaries with coverage_verified=false",
        "deferred_output": ["engagement_state", "behavioral_risk_score", "member_activity_segment", "churn_probability"]}
    (reports / "readiness.json").write_text(json.dumps(readiness, indent=2) + "\n", encoding="utf-8")
    result = {"synthetic": True, "analysis_date": "2026-10-18", "snapshots": len(cutoffs), "member_snapshot_rows": len(panel), "first_cutoff": str(cutoffs[0]), "last_cutoff": str(cutoffs[-1]), "final_roster": len(final), "final_represented": int(final_summary.members_with_exported_history), "calendar_eligible_90d_final": len(sensitivity), "baseline_sign_disagreements": sign_mismatches, "figures": len(figures), "states_ready": False}
    (reports / "summary.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    versions = {"python": platform.python_version(), **{p: importlib.metadata.version(p) for p in ["numpy", "pandas", "matplotlib", "nbformat", "nbclient"]}}
    (reports / "environment.json").write_text(json.dumps(versions, indent=2) + "\n", encoding="utf-8")
    report = f"""# Longitudinal attendance exploration — Observe extension

**Gym Member Behavior & Engagement Intelligence · 18 October 2026**

**Synthetic selected public sample. Capture remains unverified. No states, thresholds, segmentation, risk scores or churn model are produced.** This extends the observation milestone with repeated historical summaries; it does not satisfy the completeness gates for state calibration. The source revision and raw files are unchanged from Milestone 1.

## What changed

Reconstructed **{len(cutoffs)} exclusive cutoffs**, from **{cutoffs[0].date()}** through **{cutoffs[-1].date()}**, yielding **{len(panel):,} member-snapshot rows**. Calendar month-end snapshots use the next month's midnight; the final {cutoffs[-1].date()} cutoff is explicitly a partial-month boundary. Metrics retain fixed trailing 7/30/90-day windows, not calendar-month counts. Each snapshot includes only roster members signed up and exported events strictly before that cutoff. Later events cannot turn an earlier unknown member into a represented member. The roster itself is a retrospective snapshot, so event-time filtering is not a claim of historical data availability: ingestion timestamps and backfill history are absent.

## Support before interpretation

At the final cutoff: {len(final)} signed-up roster rows, {int(final_summary.members_with_exported_history)} members with exported history, {int(final_summary.no_exported_history)} with no exported history, and **0 with verified capture**. Calendar eligibility requires exported history, sufficient signup age and a nominal window inside the earliest pre-cutoff exported date. This is a conservative span check, not evidence of acquisition completeness or entitlement.

{md_table(summary[['as_of_exclusive', 'signed_up_roster', 'members_with_exported_history', 'calendar_eligible_30d', 'calendar_eligible_60d', 'calendar_eligible_90d']])}

## Within-member count changes

The final 60-day calendar-eligible cohort contains **{int(final_summary.calendar_eligible_60d)} members**. Current-minus-previous 30-day exported counts are positive for **{int(final_summary.positive_30d_count_changes)}**, equal for **{int(final_summary.zero_30d_count_changes)}**, and negative for **{int(final_summary.negative_30d_count_changes)}**. These are arithmetic count comparisons. Equality does not establish Stable; a negative difference does not establish Declining; zeros do not establish Dormant. Cancelled memberships remain in these descriptive export summaries; entitlement is not inferred and outreach eligibility is not produced.

An illustration selected deterministically from the smallest non-zero current count shared by members with different changes:

{md_table(example_frame) if not example_frame.empty else 'No qualifying same-volume pair exists at this cutoff.'}

This illustrates information lost by current volume alone, without asserting engagement or causal explanations. The heatmap shows changes at each historical cutoff; gray cells are unavailable comparisons.

## Window and baseline sensitivity

The matched cohort with 90 days of calendar opportunity contains **{len(sensitivity)} members**. Comparing the sign of current30 − previous30 with current30 − preceding60/2 yields **{sign_mismatches} disagreements ({sign_mismatches/len(sensitivity):.1%})**. Zero is treated as a distinct arithmetic sign. Disagreement is definition sensitivity, not misclassification against ground truth. The 90-day rate includes the latest 30 days and is therefore statistically dependent on the 30-day rate; their comparison is descriptive, not an independent validation. No thresholds are selected from these small synthetic distributions.

## Feature diagnostics

All roster nulls and represented-row summaries are shown separately. Zero fraction uses non-null represented rows; missing members are never filled with zero. Quantiles and distinct counts are descriptive diagnostics, not engagement thresholds.

{md_table(diagnostics.round(3))}

Branch diversity is structurally limited in this source: it counts distinct exported branches, and the inspected events never leave members' home branches. A low-information feature in this sample may still be useful in a real chain with verified multi-branch visits. Low variability across zero-export weeks does not establish a stable habit.

## Readiness and next work

Three input requirements remain unmet: verified member-level capture intervals; source timezone; effective access and operating calendars. See [readiness evidence](readiness.json) and [input template](../../handoff/observation_coverage_template.csv). The empty template contains column headers only, not invented coverage rows. Source cancellation fields cannot fill these acquisition gaps. Obtaining those fields is the next gate before state/threshold calibration. Meanwhile the code can reproduce descriptive historical metrics and test temporal filtering.

The secondary Kaggle dataset remains deferred and is not merged with this source. No purchase, external publication or real-member outreach is part of this work. The methodological findings are transferable; the numerical values are synthetic and sample-specific. Snapshot rows are repeated measures, not independent members; no significance tests, prediction performance or real-gym generalization is claimed.

## Reproduction and output contract

Run `python scripts/analyze_longitudinal.py`, then execute the generated `03b_longitudinal_eda.ipynb`. Outputs are under `data/processed/longitudinal/`. [Schema and definitions](../../docs/longitudinal_methodology.md) cover the existing 29 metric fields and six new snapshot metadata fields. The original [Milestone 1 report](../milestone_1.md) remains available.

## Figures

"""
    for name, title in figures:
        report += f"### {title}\n\n![{title}](figures/{name}.png)\n\n"
    (reports / "report.md").write_text(report, encoding="utf-8")
    gallery = "".join(f'<section><h2>{html.escape(title)}</h2><img alt="{html.escape(title)}" src="data:image/png;base64,{base64.b64encode((reports / f"figures/{name}.png").read_bytes()).decode()}"></section>' for name, title in figures)
    page = f'''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>OGDT · Longitudinal attendance exploration</title><style>body{{font:16px/1.6 system-ui;background:#f1f4f7;color:#172a3a;margin:0}}main{{max-width:1100px;padding:36px 24px;margin:auto}}h1{{font-size:clamp(30px,5vw,48px);line-height:1.15}}.note{{background:#fff1d8;border-left:5px solid #d06b2d;padding:20px}}section{{margin:24px 0;padding:20px;background:white;border-radius:10px}}img{{width:100%;height:auto}}pre{{white-space:pre-wrap;font:14px/1.6 system-ui}}a{{color:#235789}}</style><main><p>OPEN GYM DIGITAL TWIN / OBSERVE EXTENSION</p><h1>Attendance changes over time.<br>So does the evidence available.</h1><p>18 October 2026 · {len(cutoffs)} historical cutoffs · {len(panel):,} member snapshots · 5 new figures</p><div class="note"><strong>Synthetic public sample; zero verified member capture windows.</strong><br>All results describe exported events. Engagement states, segmentation and risk remain deferred pending complete capture, timezone and access context.</div><p>{sign_mismatches} of {len(sensitivity)} comparable members have different arithmetic change signs when the baseline definition changes. These are not validated behavioral classifications.</p><p><a href="report.md">Full narrative</a> · <a href="readiness.json">Readiness evidence</a> · <a href="../../docs/longitudinal_methodology.md">Definitions</a> · <a href="../milestone_1.html">Milestone 1</a></p>{gallery}<section><h2>Narrative and numerical tables</h2><pre>{html.escape(report.split('## Figures')[0])}</pre></section></main></html>'''
    (reports / "report.html").write_text(page, encoding="utf-8")
    cells = [nbf.v4.new_markdown_cell("# 03b · Longitudinal attendance exploration\n\n**Synthetic selected public sample · observation extension.** No states, thresholds, clusters or risk scores. Monthly event-time snapshots do not establish verified capture or point-in-time ingestion availability."),
             nbf.v4.new_code_cell('from pathlib import Path\nimport sys\nimport pandas as pd\nfrom IPython.display import display, Image\nROOT = Path.cwd()\nif not (ROOT / "src").is_dir(): ROOT = ROOT.parent\nsys.path.insert(0, str(ROOT))\nfrom src.data.load import load_tables\nfrom src.features.longitudinal import observation_cutoffs, longitudinal_metrics\ntables = load_tables(ROOT)\npanel = longitudinal_metrics(tables["members"], tables["checkins"], observation_cutoffs(tables["checkins"]))\nprint("Synthetic member-snapshot rows:", len(panel))\nassert not panel.coverage_verified.any()\ndisplay(panel.head())'),
             nbf.v4.new_code_cell('for name in ["snapshot_summary", "feature_diagnostics", "window_sensitivity", "same_volume_different_history"]:\n    print(name)\n    display(pd.read_csv(ROOT / f"data/processed/longitudinal/{name}.csv"))'),
             nbf.v4.new_code_cell('for path in sorted((ROOT / "reports/longitudinal/figures").glob("*.png")):\n    display(Image(filename=str(path)))'),
             nbf.v4.new_markdown_cell("## Interpretation and next gate\n\nCurrent attendance volume alone loses within-member history. Baseline choices can change a count-change sign; this is not a validated state. Unknown coverage remains unknown in every snapshot. Retrospective roster availability and overlapping windows prevent prospective or independent-validation claims. Obtain member capture intervals, source timezone and access/closure calendars before calibrating states. See docs/longitudinal_methodology.md and reports/longitudinal/readiness.json.")]
    nb = nbf.v4.new_notebook(cells=cells, metadata={"kernelspec": {"name": "python3", "display_name": "Python 3", "language": "python"}, "ogdt": {"synthetic": True, "scope": "observe_extension"}})
    nbf.write(nb, ROOT / "notebooks/03b_longitudinal_eda.ipynb")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
