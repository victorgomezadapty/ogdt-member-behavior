"""Verify downloaded evidence of the completed private Kaggle execution."""
from pathlib import Path
import hashlib
import json
import nbformat

ROOT = Path(__file__).resolve().parents[1]


def main():
    runtime = ROOT / "reports/kaggle-runtime"
    package = ROOT / "publication/kaggle"
    metadata = json.loads((runtime / "submitted/kernel-metadata.json").read_text(encoding="utf-8"))
    local = nbformat.read(package / "ogdt_monthly_behavior.ipynb", as_version=4)
    remote = nbformat.read(runtime / "submitted" / metadata["code_file"], as_version=4)
    nbformat.validate(local)
    nbformat.validate(remote)
    assert [c.source for c in local.cells] == [c.source for c in remote.cells], "Remote source differs"
    assert metadata["is_private"] is True and metadata["enable_internet"] is True
    assert not any(metadata.get(key) for key in ["dataset_sources", "competition_sources", "kernel_sources", "model_sources"])
    build = json.loads((package / "build_manifest.json").read_text(encoding="utf-8"))
    digest = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
    assert digest(package / "ogdt_monthly_behavior.ipynb") == build["notebook_sha256"]
    assert all(digest(ROOT / path) == sha for path, sha in build["source_code_sha256"].items())
    log_path = runtime / "ogdt-member-behavior-monthly-gym-attendance.log"
    log = json.loads(log_path.read_text(encoding="utf-8"))
    stdout = "".join(item["data"] for item in log if item.get("stream_name") == "stdout")
    environment, _ = json.JSONDecoder().raw_decode(stdout.lstrip())
    assert set(environment) == {"python", "numpy", "pandas", "matplotlib"}
    summary = json.loads((runtime / "ogdt_aggregate_summary.json").read_text(encoding="utf-8"))
    expected = json.loads((ROOT / "reports/berkeley/summary.json").read_text(encoding="utf-8"))
    mapping = {"source_rows": "source_rows", "source_members": "source_members", "eligible_rows": "eligible_rows",
               "eligible_members": "eligible_members", "recorded_events": "recorded_events_in_eligible_rows",
               "mean_attendance": "mean_attendance_per_eligible_month", "zero_fraction": "zero_recorded_fraction",
               "adjacent_comparisons": "adjacent_comparisons", "complete_3_month_windows": "complete_3_month_windows",
               "complete_6_month_windows": "complete_6_month_windows"}
    assert all(summary[a] == expected[b] for a, b in mapping.items()), "Remote/local parity failed"
    assert summary["member_level_outputs_written"] is False
    outputs = sorted(p.name for p in runtime.iterdir() if p.is_file() and p.suffix != ".log")
    assert outputs == ["ogdt_aggregate_summary.json", "ogdt_monthly_aggregates.png"]
    assert not any(c.get("outputs") for c in local.cells if c.cell_type == "code")
    report = {"validated_on": "2026-10-20", "kernel": metadata["id"], "kernel_id": metadata["id_no"],
              "url": "https://www.kaggle.com/code/" + metadata["id"], "version": 1,
              "remote_status": "COMPLETE", "status_evidence": "Kaggle CLI kernels status returned KernelWorkerStatus.COMPLETE",
              "is_private": metadata["is_private"], "environment": environment, "docker_image": metadata.get("docker_image"),
              "remote_source_matches_package": True, "local_remote_aggregate_parity": True,
              "source_code_sha256": build["source_code_sha256"], "notebook_sha256": build["notebook_sha256"],
              "downloaded_log_sha256": digest(log_path),
              "output_sha256": {name: digest(runtime / name) for name in outputs},
              "outputs": outputs, "summary": summary, "data_bundled": False,
              "raw_or_member_level_outputs": False, "public_release_performed": False,
              "visual_qa": "aggregate PNG inspected; readable labels and no clipped panels"}
    (ROOT / "reports/berkeley/kaggle_validation.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"private": True, "status": "COMPLETE", "aggregate_parity": True, "environment": environment}))


if __name__ == "__main__":
    main()
