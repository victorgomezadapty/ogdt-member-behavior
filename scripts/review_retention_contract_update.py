"""Explicit review of the observed admission-status-only Retention contract change."""
from pathlib import Path
import copy
import hashlib
import json
import subprocess
import sys
import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.data.berkeley import load_berkeley
from src.data.retention_bridge import inspect_retention_bridge


def main():
    retention = ROOT.parent / "ogdt-retention"
    previous_sha = "7a699000dcbbef7f3dd062b032c4a6b96cfeb549e7f30aa72f4c0e89a74c3373"
    previous = subprocess.check_output(["git", "-C", str(retention), "show", "1f04bf6:handoff/data_contract.yaml"])
    assert any(hashlib.sha256(v).hexdigest() == previous_sha for v in [previous, previous.replace(b"\r\n", b"\n").replace(b"\n", b"\r\n")])
    old = yaml.safe_load(previous)
    new = yaml.safe_load((retention / "handoff/data_contract.yaml").read_text(encoding="utf-8"))
    stripped_old, stripped_new = copy.deepcopy(old), copy.deepcopy(new)
    for data in [stripped_old, stripped_new]:
        data.pop("status")
        for key in ["core_admission", "reviewed_lab_revision", "core_revision", "trained_model_extracted"]:
            data["integration"].pop(key, None)
    assert stripped_old == stripped_new, "Unexpected semantic change; do not refresh fingerprints"
    assert new["integration"]["trained_model_extracted"] is False
    source, _ = load_berkeley(ROOT / "data/raw/berkeley/data.zip")
    features = pd.read_csv(ROOT / "data/processed/berkeley/member_month_metrics.csv", dtype={"member_id": str}, parse_dates=["period_end", "as_of_exclusive"])
    path = ROOT / "reports/berkeley/integration_readiness.json"
    result = json.loads(path.read_text(encoding="utf-8"))
    current = inspect_retention_bridge(features, source, retention)
    assert current["retention_features_sha256"] == result["retention_features_sha256"], "Export changed"
    result.update(current)
    result["contract_change_review"] = {"date": "2026-10-20", "previous_contract_sha256": previous_sha,
        "decision": "accept editorial core-admission status and revision metadata only; all other YAML semantics equal",
        "feature_export_unchanged": True, "core_uses_original_reviewed_snapshot_for_ADR014": True}
    path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result["contract_change_review"]))


if __name__ == "__main__":
    main()
