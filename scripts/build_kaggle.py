"""Build a code-only, self-contained notebook from the reviewed lab functions."""
from pathlib import Path
import hashlib
import json
import nbformat as nbf

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "publication/kaggle"


def build():
    OUT.mkdir(parents=True, exist_ok=True)
    paths = ["src/data/berkeley.py", "src/features/monthly.py"]
    hashes = {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in paths}
    code = "\n\n".join("\n".join(line for line in (ROOT / p).read_text(encoding="utf-8").splitlines()
                                      if not line.startswith("from src.data.berkeley import")) for p in paths)
    cells = [nbf.v4.new_markdown_cell("""# OGDT Member Behavior: Monthly Gym Attendance

Real historical fitness data from Stefano DellaVigna and Ulrike Malmendier,
[Paying Not to Go to the Gym](https://eml.berkeley.edu/~sdellavi/data/gymdata.shtml).
This notebook studies recorded attendance trajectories, with **unknown months kept distinct from recorded zeros**.
It is a descriptive research component of Open Gym Digital Twin, not a validated engagement or churn model.

The original study already examines attendance and contracts. Our contribution is a reusable, audited
12-metric monthly interface, gap-aware windows and explicit integration boundaries. We do not claim a new
scientific discovery or reproduce the paper's 7,752-member sample.

The source is downloaded directly from the author's site into temporary storage and checked by SHA-256.
No source files or member-level exports are bundled or written to notebook outputs. Public access to the
source is not an explicit redistribution license. Code licensing does not grant rights to the underlying data.
Enable Internet on Kaggle. Alternatively set `OGDT_BERKELEY_ARCHIVE` to a lawfully obtained local ZIP.
"""), nbf.v4.new_code_cell("""from pathlib import Path
import os, json, tempfile, urllib.request, platform, importlib.metadata
from IPython.display import display
print(json.dumps({"python": platform.python_version(), **{p: importlib.metadata.version(p) for p in ["numpy", "pandas", "matplotlib"]}}, indent=2))
"""), nbf.v4.new_code_cell(code), nbf.v4.new_markdown_cell("""## Eligibility before metrics

The raw table contains calendar padding, nonregular contracts and excluded months.
Select contract codes 1/2, accepted duplicate/problem/overtime flags, and the intersection of
source attendance bounds and the published club spans. These retrospective flags define selection;
they are not predictors available in a live system. The clock is an assumed month-close proxy.
Missing or excluded months break histories. Three/six-month windows require every month to be eligible.
"""), nbf.v4.new_code_cell("""with tempfile.TemporaryDirectory(prefix="ogdt-source-") as temporary:
    supplied = os.environ.get("OGDT_BERKELEY_ARCHIVE")
    if supplied:
        archive_path = Path(supplied)
    else:
        archive_path = Path(temporary) / "source.zip"
        request = urllib.request.Request("https://eml.berkeley.edu/~sdellavi/data/data.zip", headers={"User-Agent": "OGDT-research-notebook/1.0"})
        with urllib.request.urlopen(request, timeout=90) as response:
            content = response.read(10_000_001)
        if len(content) > 10_000_000:
            raise ValueError("Unexpected source archive size")
        archive_path.write_bytes(content)
    source, labels = load_berkeley(archive_path)
audit = monthly_observations(source)
features = monthly_metrics(audit)
assert len(source) == 491506 and source.id.nunique() == 10241
assert len(features) == 84251 and features.member_id.nunique() == 8073
assert int(features.recorded_attendance_month.sum()) == 397354
assert audit.loc[~audit.attendance_eligible, "recorded_attendance_month"].isna().all()
assert not features.synthetic.any()
summary = {"source_rows": len(source), "source_members": int(source.id.nunique()),
           "eligible_rows": len(features), "eligible_members": int(features.member_id.nunique()),
           "recorded_events": int(features.recorded_attendance_month.sum()),
           "mean_attendance": float(features.recorded_attendance_month.mean()),
           "zero_fraction": float(features.recorded_attendance_month.eq(0).mean()),
           "adjacent_comparisons": int(features.attendance_previous_month.notna().sum()),
           "complete_3_month_windows": int(features.attendance_sum_3_calendar_months.notna().sum()),
           "complete_6_month_windows": int(features.attendance_sum_6_calendar_months.notna().sum()),
           "source_sha256": ARCHIVE_SHA256, "selection_policy": POLICY_ID,
           "synthetic": False, "operational_use_allowed": False,
           "member_level_outputs_written": False}
assert summary["adjacent_comparisons"] == 73352
assert summary["complete_3_month_windows"] == 64347
assert summary["complete_6_month_windows"] == 43690
print(json.dumps(summary, indent=2))
support = features[FEATURE_COLUMNS].agg(["count", "mean", "median"]).T
support.index.name = "metric"
display(support)
Path("ogdt_aggregate_summary.json").write_text(json.dumps(summary, indent=2) + "\\n", encoding="utf-8")
"""), nbf.v4.new_code_cell("""import matplotlib.pyplot as plt
monthly = features.groupby(["period_end", "club_id"]).agg(
    eligible_rows=("member_id", "size"), mean_attendance=("recorded_attendance_month", "mean")).reset_index()
fig, axes = plt.subplots(2, 2, figsize=(13, 8))
for club, group in monthly.groupby("club_id"):
    axes[0, 0].plot(group.period_end, group.eligible_rows, label=f"Club {club}")
    axes[0, 1].plot(group.period_end, group.mean_attendance, label=f"Club {club}")
axes[0, 0].set_title("Eligible monthly observations — changing population")
axes[0, 1].set_title("Recorded attendance / eligible month")
axes[0, 0].legend()
axes[1, 0].hist(features.recorded_attendance_month, bins=range(0, 51), color="#235789")
axes[1, 0].set_title("Monthly counts (display range 0–50)")
axes[1, 1].barh(["Current month", "Adjacent month", "Complete 3 months", "Complete 6 months"],
               [84251, 73352, 64347, 43690], color="#16817a")
axes[1, 1].set_title("Metric support: non-null member-month rows")
fig.suptitle("OGDT · Real historical Berkeley data · regular-month descriptive subset")
fig.tight_layout()
fig.savefig("ogdt_monthly_aggregates.png", dpi=140)
plt.show()
"""), nbf.v4.new_markdown_cell("""## Connection to the gym digital twin

This is the historical monthly **observation layer**: counts, changes, rolling volume, variability and
history support. It cannot reconstruct daily visits, peak hours, physical occupancy or true membership tenure.
Monthly recency is not days since a visit. Zero variability may describe repeated zeros, not a strong habit.

The separate OGDT Retention lab uses the same pinned source. Local integration verified all 81,927
of its eligible member-month keys/current counts. Our 2,324 additional rows reflect its family-as-of
exclusion. Retention also allows prior prorated months in some histories; this notebook requires regular
months throughout. These metrics must not silently replace its trained model's inputs. This standalone
notebook does not read Retention labels, scores or local reports, and does not independently repeat that join.

**Limits:** historical three-club population; selection and capture assumptions; no verified ingestion clock,
uncertainty interval, validated engagement states, prediction, intervention effect or current-gym validation.
The mean is weighted by eligible member-month observations, not equally by people. A recorded zero only
applies to an eligible month. Source dates and author flags condition retrospective eligibility.

**Attribution:** Stefano DellaVigna and Ulrike Malmendier (2006), *Paying Not to Go to the Gym*,
American Economic Review, 96(3), 694–719. [Author data page](https://eml.berkeley.edu/~sdellavi/data/gymdata.shtml).
OGDT code and methodology: OGDT contributors. Underlying data retain their own rights; no data license inferred.
""")]
    notebook = nbf.v4.new_notebook(cells=cells, metadata={"kernelspec": {"name": "python3", "display_name": "Python 3", "language": "python"}, "ogdt": {"source_code_sha256": hashes, "data_bundled": False}})
    nbf.write(notebook, OUT / "ogdt_monthly_behavior.ipynb")
    metadata = {"id": "vctorandrsgmezlpez/ogdt-member-behavior-monthly-gym-attendance", "title": "OGDT Member Behavior Monthly Gym Attendance", "code_file": "ogdt_monthly_behavior.ipynb", "language": "python", "kernel_type": "notebook", "is_private": True, "enable_gpu": False, "enable_internet": True, "dataset_sources": [], "competition_sources": [], "kernel_sources": []}
    (OUT / "kernel-metadata.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    (OUT / "build_manifest.json").write_text(json.dumps({"source_code_sha256": hashes, "notebook_sha256": hashlib.sha256((OUT / "ogdt_monthly_behavior.ipynb").read_bytes()).hexdigest(), "data_bundled": False}, indent=2) + "\n", encoding="utf-8")
    print("Built standalone code-only Kaggle package")


if __name__ == "__main__":
    build()
