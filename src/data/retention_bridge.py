"""Read-only feature compatibility audit; outcomes and scores are not imported."""
from pathlib import Path
import hashlib
import numpy as np
import pandas as pd
import yaml
from src.data.berkeley import ARCHIVE_SHA256, TABLE_SHA256, KEY, DATASET_ID, matlab_dates, assert_same_population


def inspect_retention_bridge(behavior, source, retention_root):
    root = Path(retention_root)
    path = root / "data/processed/berkeley/monthly_features.csv"
    contract_path = root / "handoff/data_contract.yaml"
    if not path.exists() or not contract_path.exists():
        return {"retention_canonical_export_available": False, "retention_outcomes_imported": False,
                "verified_scope": "source identity and original population keys only; canonical export absent"}
    contract = yaml.safe_load(contract_path.read_text(encoding="utf-8"))
    archive = root / contract["primary_source"]["local_file"]
    if hashlib.sha256(archive.read_bytes()).hexdigest() != ARCHIVE_SHA256:
        raise ValueError("Retention source archive changed; reassess population before joining")
    columns = KEY + ["attend", "snapshot_eligible", "prediction_date", "log_visits_previous", "log_visits_mean_3m"]
    current = pd.read_csv(path, usecols=columns, dtype={"member_id": str}, parse_dates=["period_end", "prediction_date"])
    assert_same_population(behavior, current, TABLE_SHA256, TABLE_SHA256)
    joined = behavior.merge(current, on=KEY, how="outer", indicator=True, validate="one_to_one")
    both = joined[joined._merge.eq("both")]
    unmatched = joined[joined._merge.eq("left_only")]
    raw = source.sort_values(["id", "time"]).copy()
    family_now = ((raw.club.eq(11) & raw.code.isin([8,114,95,210,143,235,249])) |
                  (raw.club.ne(11) & raw.code.isin([29,154,187,69,269,9999,281,252,253])))
    family_asof = family_now.groupby(raw.id, sort=False).cummax()
    family_keys = pd.DataFrame({"dataset_id":DATASET_ID,"member_id":raw.id.astype("int64").astype(str),
                                "period_end":matlab_dates(raw.time).dt.to_period("M").dt.to_timestamp("M"),
                                "family_observed_asof":family_asof})
    unmatched_with_reason = unmatched[KEY].merge(family_keys, on=KEY, how="left", validate="one_to_one")
    # The timestamp representations have different names but the same month boundary.
    boundary_equal = both.as_of_exclusive.eq(both.prediction_date + pd.Timedelta(nanoseconds=1))
    previous_joint = both.attendance_previous_month.notna() & both.log_visits_previous.notna()
    mean_joint = both.attendance_mean_3_calendar_months.notna() & both.log_visits_mean_3m.notna()
    checks = {
        "retention_keys_are_subset_of_behavior_keys": not joined._merge.eq("right_only").any(),
        "matched_current_attendance_equal": both.recorded_attendance_month.eq(both.attend).all(),
        "retention_export_marks_snapshots_eligible": current.snapshot_eligible.eq(True).all(),
        "month_close_boundaries_equivalent": boundary_equal.all(),
        "behavior_only_rows_explained_by_family_asof": unmatched_with_reason.family_observed_asof.eq(True).all(),
        "joint_previous_counts_agree_after_inverse_log": np.isclose(both.loc[previous_joint,"attendance_previous_month"],np.expm1(both.loc[previous_joint,"log_visits_previous"]),atol=1e-8).all(),
        "joint_three_month_means_agree_after_inverse_log": np.isclose(both.loc[mean_joint,"attendance_mean_3_calendar_months"],np.expm1(both.loc[mean_joint,"log_visits_mean_3m"]),atol=1e-8).all()}
    if not all(checks.values()):
        raise ValueError(f"Retention bridge needs semantic review: {[k for k,v in checks.items() if not v]}")
    return {"checked_at":"2026-10-20", "retention_canonical_export_available":True,
            "retention_contract_version":contract["contract_version"],
            "retention_existing_target_version":contract["outcomes"]["target_version"],
            "retention_existing_historical_model":contract["model"]["trained_on_current_real_source"],
            "retention_features_sha256":hashlib.sha256(path.read_bytes()).hexdigest(),
            "retention_contract_sha256":hashlib.sha256(contract_path.read_bytes()).hexdigest(),
            "retention_feature_rows":len(current),"matched_canonical_rows":len(both),
            "behavior_only_rows":len(unmatched),"retention_only_rows":int(joined._merge.eq("right_only").sum()),
            "behavior_only_explanation":"family_observed_asof in Retention; Member Behavior keeps a broader regular-month subset",
            "previous_history_available_only_in_retention":int((both.attendance_previous_month.isna() & both.log_visits_previous.notna()).sum()),
            "three_month_history_available_only_in_retention":int((both.attendance_mean_3_calendar_months.isna() & both.log_visits_mean_3m.notna()).sum()),
            "history_policy_difference":"Retention allows prior prorated 11/21 months inside episodes; Behavior requires regular 1/2 months throughout its windows",
            "model_feature_substitution_allowed":False,
            "retention_outcomes_imported":False,"new_model_trained_here":False,"other_populations_joined":False,
            "checks":{k:bool(v) for k,v in checks.items()},
            "verified_scope":"read-only canonical feature-key, current-count and boundary comparison; no outcomes/scores joined"}
