"""Verify the active monthly adapter without requiring synthetic sandbox rebuilds."""
from pathlib import Path
import json
import re
import subprocess
import sys
import hashlib
import pandas as pd
import nbformat
import yaml

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from src.data.berkeley import DATASET_ID, ARCHIVE_SHA256, TABLE_SHA256, KEY, load_berkeley
from src.features.monthly import FEATURE_COLUMNS


def main():
    reports=ROOT/"reports/berkeley"
    tests=subprocess.run([sys.executable,"-m","unittest","discover","-s","tests","-p","test_monthly.py","-v"],cwd=ROOT,capture_output=True,text=True)
    (reports/"tests.txt").write_text(tests.stdout+tests.stderr,encoding="utf-8")
    checks={"monthly_boundary_and_population_tests":tests.returncode==0}
    raw=ROOT/"data/raw/berkeley/data.zip"
    source,_=load_berkeley(raw)
    checks["pinned_source_hashes_schema_and_keys"]=len(source)==491506 and source.id.nunique()==10241
    audit=pd.read_csv(ROOT/"data/processed/berkeley/member_month_eligibility.csv",dtype={"member_id":str},parse_dates=["period_end"])
    features=pd.read_csv(ROOT/"data/processed/berkeley/member_month_metrics.csv",dtype={"member_id":str},parse_dates=["period_end","as_of_exclusive"])
    catalog=pd.read_csv(ROOT/"handoff/monthly_feature_catalog.csv")
    checks["all_source_keys_preserved_in_eligibility_audit"]=len(audit)==len(source) and not audit.duplicated(KEY).any()
    checks["regular_month_cohort_exactly_recorded"]=len(features)==84251 and features.member_id.nunique()==8073 and not features.duplicated(KEY).any()
    checks["real_source_namespace_preserved"]=features.dataset_id.eq(DATASET_ID).all() and audit.dataset_id.eq(DATASET_ID).all() and not features.synthetic.any()
    checks["ineligible_attendance_is_null_not_imputed_zero"]=audit.loc[~audit.attendance_eligible,"recorded_attendance_month"].isna().all()
    checks["feature_rows_are_exact_eligible_keys"]=features[KEY].merge(audit.loc[audit.attendance_eligible,KEY],on=KEY,how="outer",indicator=True,validate="one_to_one")._merge.eq("both").all()
    features_source=features.merge(audit[KEY+["recorded_attendance_month"]],on=KEY,validate="one_to_one",suffixes=("","_audit"))
    checks["current_counts_match_eligible_source"]=features_source.recorded_attendance_month.eq(features_source.recorded_attendance_month_audit).all()
    checks["canonical_month_end_and_cutoff"]=features.period_end.eq(features.period_end.dt.to_period("M").dt.to_timestamp("M")).all() and features.as_of_exclusive.eq(features.period_end+pd.Timedelta(days=1)).all()
    checks["catalog_covers_all_monthly_output_fields"]=set(features.columns)==set(catalog.feature) and catalog.feature.is_unique and catalog.notna().all().all()
    forbidden={"endatt","begatt","endcont","endcontp","duplicate","problem","overtime","contract","source_contract_code","birthday","age","female","trprice","imprice","churn_probability","engagement_state","days_since_last_visit","visits_30d"}
    checks["no_future_metadata_contract_outcomes_or_fabricated_daily_features"]=not forbidden.intersection(features.columns)
    checks["three_month_windows_require_full_contiguous_support"]=(features.attendance_sum_3_calendar_months.notna()==features.consecutive_eligible_months.ge(3)).all()
    checks["six_month_windows_require_full_contiguous_support"]=(features.attendance_sum_6_calendar_months.notna()==features.consecutive_eligible_months.ge(6)).all()
    checks["prior_zero_percent_change_is_null"]=features.loc[features.attendance_previous_month.eq(0),"attendance_pct_change_vs_previous_month"].isna().all()
    checks["current_count_conservation"]=int(features.recorded_attendance_month.sum())==397354 and int(audit.recorded_attendance_month.sum())==397354
    integration=json.loads((reports/"integration_readiness.json").read_text(encoding="utf-8"))
    checks["shared_population_and_original_keys_match"]=integration["archive_identity_matches"] and integration["table_sha256"]==TABLE_SHA256 and integration["matching_behavior_keys_in_original_population"]==len(features) and not integration["other_populations_joined"]
    checks["retention_outcomes_and_models_not_imported"]=not integration.get("retention_outcomes_imported",False) and not integration.get("new_model_trained_here",False)
    checks["canonical_feature_bridge_checks_pass"]=integration["retention_canonical_export_available"] and all(integration["checks"].values()) and integration["matched_canonical_rows"]==integration["retention_feature_rows"] and integration["matched_canonical_rows"]+integration["behavior_only_rows"]==len(features)
    retention_root=ROOT.parent/"ogdt-retention"
    checks["retention_export_fingerprint_still_matches"]=hashlib.sha256((retention_root/"data/processed/berkeley/monthly_features.csv").read_bytes()).hexdigest()==integration["retention_features_sha256"]
    checks["retention_contract_fingerprint_still_matches"]=hashlib.sha256((retention_root/"handoff/data_contract.yaml").read_bytes()).hexdigest()==integration["retention_contract_sha256"]
    manifest=json.loads((raw.parent/"manifest.json").read_text(encoding="utf-8"))
    if str(manifest["copied_from"]).startswith("https://"):
        # Downloaded from the author: the frozen local copy is the reference.
        checks["shared_archive_still_unchanged"]=manifest["archive_sha256"]==ARCHIVE_SHA256==hashlib.sha256(raw.read_bytes()).hexdigest()
    else:
        shared=Path(manifest["copied_from"])
        checks["shared_archive_still_unchanged"]=shared.exists() and hashlib.sha256(shared.read_bytes()).hexdigest()==ARCHIVE_SHA256
    contract=yaml.safe_load((ROOT/"handoff/monthly_data_contract.yaml").read_text(encoding="utf-8"))
    checks["contract_matches_grain_key_and_scope"]=contract["canonical_key"]==KEY and contract["source"]["synthetic"] is False and not contract["retention_boundary"]["new_model_trained"] and not contract["selection"]["reproduces_published_7752_member_sample"]
    figure_paths=list((reports/"figures").glob("*.png"))
    checks["five_real_monthly_figures"]=len(figure_paths)==5 and all(p.stat().st_size>10000 for p in figure_paths)
    nb=nbformat.read(ROOT/"notebooks/07_berkeley_monthly_eda.ipynb",as_version=4)
    nbformat.validate(nb)
    code=[c for c in nb.cells if c.cell_type=="code"]
    checks["monthly_notebook_executed_without_errors"]=bool(code) and all(c.execution_count is not None and not any(o.output_type=="error" for o in c.outputs) for c in code)
    ignored=["data/raw/berkeley/data.zip","data/processed/berkeley/member_month_metrics.csv","data/processed/berkeley/member_month_eligibility.csv"]
    ignore=subprocess.run(["git","check-ignore","--",*ignored],cwd=ROOT,capture_output=True,text=True)
    checks["raw_and_person_level_artifacts_ignored_by_git"]=set(ignore.stdout.splitlines())==set(ignored)
    broken=[]
    docs=[ROOT/"README.md",reports/"report.md",ROOT/"docs/project_plan.md",ROOT/"docs/data_readiness.md",ROOT/"docs/monthly_methodology.md",ROOT/"docs/monthly_data_dictionary.md"]
    for path in docs:
        for target in re.findall(r"\]\(([^)]+)\)",path.read_text(encoding="utf-8")):
            if target.startswith(("http","#")) or path.parent/target==reports/"verification.json":
                continue
            if not (path.parent/target).exists():
                broken.append(f"{path.name}: {target}")
    checks["new_report_and_document_links_resolve"]=not broken
    result={"all_pass":all(checks.values()),"checks":{k:bool(v) for k,v in checks.items()},"dataset_id":DATASET_ID,"synthetic":False,
        "feature_fields":len(features.columns),"behavior_metrics":len(FEATURE_COLUMNS),"eligible_rows":len(features),"eligible_members":int(features.member_id.nunique()),"broken_links":broken,
        "scope":"monthly_descriptive_research_no_target_or_model"}
    (reports/"verification.json").write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(result,indent=2))
    if not result["all_pass"]:
        print(tests.stdout+tests.stderr)
        raise SystemExit(1)


if __name__=="__main__":
    main()
