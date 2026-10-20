"""Offline source-to-artifact checks and test-suite evidence."""
from pathlib import Path
import json
import re
import subprocess
import sys
import pandas as pd
import nbformat
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.data.load import load_tables, audit_tables


def main():
    tests = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"], cwd=ROOT, capture_output=True, text=True)
    (ROOT / "reports/tests.txt").write_text(tests.stdout + tests.stderr, encoding="utf-8")
    checks = {"regression_tests": tests.returncode == 0}
    required = ["README.md", "requirements.txt", ".gitignore", "docs/data_dictionary.md", "docs/entity_relationships.md", "docs/dataset_limitations.md", "docs/methodology.md", "docs/behavioral_state_definition.md", "handoff/data_contract.yaml", "handoff/feature_catalog.csv", "handoff/metrics_definition.md", "handoff/findings.md", "handoff/limitations.md", "handoff/module_spec.md", "reports/milestone_1.html", "reports/milestone_1.md"]
    required += ["docs/longitudinal_methodology.md", "handoff/observation_coverage_template.csv", "reports/longitudinal/report.md", "reports/longitudinal/report.html", "reports/longitudinal/readiness.json"]
    checks["required_artifacts_present"] = all((ROOT / p).is_file() and (ROOT / p).stat().st_size > 0 for p in required)
    t = load_tables()
    checks["source_hashes_and_hard_audit"] = audit_tables(t)["all_hard_checks_pass"]
    metrics = pd.read_csv(ROOT / "data/processed/member_metrics.csv")
    catalog = pd.read_csv(ROOT / "handoff/feature_catalog.csv")
    checks["roster_preserved"] = len(metrics) == len(t["members"]) and metrics.member_id.is_unique and set(metrics.member_id) == set(t["members"].id)
    checks["catalog_covers_every_output_column"] = set(metrics.columns) == set(catalog.feature) and catalog.feature.is_unique and catalog.notna().all().all()
    checks["unverified_synthetic_metadata"] = metrics.synthetic.all() and not metrics.coverage_verified.any()
    unknown = metrics.sample_observation_status.eq("no_visits_in_public_sample")
    checks["sample_absence_is_null"] = int(unknown.sum()) == 268 and metrics.loc[unknown, ["visits_7d", "visits_30d", "visits_90d", "days_since_last_visit", "active_weeks_8w", "attendance_variability", "branch_diversity"]].isna().all().all()
    checks["no_contract_contact_or_state_features"] = not set(["cancel_date", "cancel_reason", "is_active", "email", "phone", "engagement_state", "behavioral_risk_score", "churn_probability"]).intersection(metrics.columns)
    n_events = len(t["checkins"])
    checks["enriched_join_preserves_events"] = len(pd.read_csv(ROOT / "data/processed/visits_enriched.csv")) == n_events
    checks["all_aggregations_conserve_events"] = all(pd.read_csv(ROOT / f"data/processed/{name}.csv")[col].sum() == n_events for name, col in [("member_month", "exported_events"), ("member_week", "exported_events"), ("monthly_summary", "exported_events"), ("day_summary", "events"), ("hour_summary", "events"), ("tenure_summary", "events"), ("branch_summary", "events"), ("plan_summary", "events")])
    timeline = pd.read_csv(ROOT / "data/processed/member_timeline.csv")
    checks["timeline_roster_and_contract_events"] = timeline.event_type.eq("signup").sum() == 300 and timeline.event_type.eq("recorded_cancel_date").sum() == 140
    notebooks = sorted((ROOT / "notebooks").glob("*.ipynb"))
    executed = deferred = 0
    notebook_valid = True
    for path in notebooks:
        nb = nbformat.read(path, as_version=4)
        nbformat.validate(nb)
        code = [c for c in nb.cells if c.cell_type == "code"]
        if path.name[:2] in ["01", "02", "03", "07"]:
            executed += 1
            notebook_valid &= bool(code) and all(c.execution_count is not None and not any(o.output_type == "error" for o in c.outputs) for c in code)
        else:
            deferred += 1
            notebook_valid &= not code and "deferred" in nb.cells[0].source.lower()
    checks["five_executed_notebooks_three_deferred"] = notebook_valid and executed == 5 and deferred == 3
    panel = pd.read_csv(ROOT / "data/processed/longitudinal/member_snapshots.csv", parse_dates=["as_of_exclusive", "first_observed_visit", "last_observed_visit"])
    snapshot_summary = pd.read_csv(ROOT / "data/processed/longitudinal/snapshot_summary.csv")
    checks["snapshot_composite_keys"] = not panel.duplicated(["member_id", "as_of_exclusive"]).any() and panel.as_of_exclusive.nunique() == 24
    join = panel.merge(t["members"][["id", "signup_date"]], left_on="member_id", right_on="id", validate="many_to_one")
    checks["snapshots_exclude_future_signup_and_events"] = (join.signup_date < join.as_of_exclusive).all() and (panel.last_observed_visit.isna() | (panel.last_observed_visit < panel.as_of_exclusive)).all()
    no_history = panel.sample_observation_status.eq("no_visits_in_public_sample")
    checks["snapshot_unknown_attendance_stays_null"] = panel.loc[no_history, ["visits_30d", "days_since_last_visit", "active_weeks_8w"]].isna().all().all() and not panel.coverage_verified.any()
    extras = {"export_span_start_as_of", "window_inside_export_span_30d", "window_inside_export_span_60d", "window_inside_export_span_90d", "consistency_inside_export_span", "snapshot_boundary"}
    checks["snapshot_schema_documented"] = set(panel.columns) == set(metrics.columns) | extras
    expected_rows = sum((t["members"].signup_date < cutoff).sum() for cutoff in panel.as_of_exclusive.unique())
    checks["historical_roster_conservation"] = len(panel) == expected_rows and snapshot_summary.signed_up_roster.sum() == expected_rows
    checks["change_summary_denominators"] = snapshot_summary[["positive_30d_count_changes", "zero_30d_count_changes", "negative_30d_count_changes"]].sum(axis=1).equals(snapshot_summary.calendar_eligible_60d)
    extension_figures = list((ROOT / "reports/longitudinal/figures").glob("*.png"))
    checks["five_longitudinal_figures"] = len(extension_figures) == 5 and all(p.stat().st_size > 10000 for p in extension_figures)
    readiness = json.loads((ROOT / "reports/longitudinal/readiness.json").read_text(encoding="utf-8"))
    checks["readiness_preserves_unmet_capture_gates"] = not readiness["operational_states_ready"] and not readiness["threshold_calibration_ready"] and len(readiness["unmet_requirements"]) == 3
    template = pd.read_csv(ROOT / "handoff/observation_coverage_template.csv")
    checks["capture_template_has_no_invented_rows"] = template.empty and {"member_id", "capture_complete", "evidence_reference"}.issubset(template.columns)
    figures = list((ROOT / "reports/figures").glob("*.png"))
    checks["eleven_figures"] = len(figures) == 11 and all(p.stat().st_size > 10000 for p in figures)
    contract = yaml.safe_load((ROOT / "handoff/data_contract.yaml").read_text(encoding="utf-8"))
    checks["contract_matches_source"] = contract["source"]["member_roster_rows"] == len(t["members"]) and contract["source"]["checkin_rows"] == n_events and contract["synthetic_demo"]
    # Internal report/document links should resolve in the delivered directory.
    broken = []
    for path in (ROOT / "docs").glob("*.md"):
        for target in re.findall(r"\]\(([^)]+)\)", path.read_text(encoding="utf-8")):
            if not target.startswith(("http", "#")) and not (path.parent / target).exists():
                broken.append(f"{path.name}: {target}")
    for path in [ROOT / "README.md", *list((ROOT / "handoff").glob("*.md")), ROOT / "reports/milestone_1.md", ROOT / "reports/longitudinal/report.md"]:
        for target in re.findall(r"\]\(([^)]+)\)", path.read_text(encoding="utf-8")):
            if path.parent / target == ROOT / "reports/verification.json":
                continue  # This verifier writes its own report after completing link checks.
            if not target.startswith(("http", "#")) and not (path.parent / target).exists():
                broken.append(f"{path.name}: {target}")
    checks["internal_document_links"] = not broken
    result = {"all_pass": all(checks.values()), "checks": {k: bool(v) for k, v in checks.items()}, "broken_links": broken, "feature_columns": len(metrics.columns), "executed_notebooks": executed, "deferred_notebooks": deferred, "visual_inspection": {"contact_sheet": "reports/visual_qa.png", "figures_reviewed": sorted(p.name for p in figures)}}
    (ROOT / "reports/verification.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    if not result["all_pass"]:
        print(tests.stdout + tests.stderr)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
