# OGDT Member Behavior Lab

## Gym Member Behavior & Engagement Intelligence

A research laboratory of **Open Gym Digital Twin: Observe → Connect → Predict → Simulate → Decide**.

**20 October completion:** [standalone Kaggle package](publication/kaggle/README.md), actually executed
in a private Kaggle notebook with local/remote aggregate parity ([evidence](reports/berkeley/kaggle_validation.json)).
84,251 regular member-months / 8,073 members; no raw data bundled. Public redistribution rights for the data
are not established; see [publication review](docs/publication_review.md). The complete active six-document
handoff is indexed in [monthly module specification](handoff/monthly_module_spec.md). Core admission is
tracked independently under `BEH-20261020-01` / ADR-015 in the sibling core; it grants descriptive research only.

**Active research, 19 October 2026: real monthly fitness behavior using Berkeley.** Source fitness suitability, population identity, granularity, capture and temporal limits were reviewed before implementation in [project plan](docs/project_plan.md) and [data readiness](docs/data_readiness.md). The primary output is a descriptive monthly adapter compatible with Retention's source identity. No machine learning, validated states, segmentation, behavioral risk scoring or contractual churn prediction is implemented.

**Preserved synthetic sandbox:** Milestone 1 and the 18 October Observe extension use Mindweave synthetic sample data. Those reports remain software/methodology evidence, separate from the real monthly research. No files were deleted and no populations were row-merged.

The central question: **What can attendance behavior tell us about member engagement before we know whether the member will cancel?** Attendance is observable behavior; engagement is a latent interpretation; behavioral disengagement is a change in behavior; retention is continued contractual participation; churn is a contractual outcome. These concepts are related and must remain distinct.

### Results to review

- **Active:** [Real monthly fitness report — Berkeley](reports/berkeley/report.html), [source dictionary](docs/monthly_data_dictionary.md), [monthly definitions](docs/monthly_methodology.md), [source audit](reports/berkeley/source_audit.json), [verification](reports/berkeley/verification.json).
- **Active handoff:** [monthly data contract](handoff/monthly_data_contract.yaml), [feature catalog](handoff/monthly_feature_catalog.csv), [integration readiness](reports/berkeley/integration_readiness.json). The file `handoff/data_contract.yaml` remains scoped to the preserved synthetic event adapter.

### Preserved synthetic results

- [Visual report — 11 figures](reports/milestone_1.html) (self-contained, open locally).
- [Analytical report with tables](reports/milestone_1.md).
- [Data dictionary](docs/data_dictionary.md), [entity relationships](docs/entity_relationships.md), [limitations](docs/dataset_limitations.md), [methodology](docs/methodology.md).
- Four executed observation notebooks in `notebooks/`, including the longitudinal extension; three explicitly deferred notebooks for later work.
- [Longitudinal exploration — 5 additional figures](reports/longitudinal/report.html), [methodology](docs/longitudinal_methodology.md), and [capture readiness evidence](reports/longitudinal/readiness.json).
- [Handoff](handoff/module_spec.md): data contract, feature catalog, definitions, findings, limitations, module specification.
- Machine-readable [audit](reports/data_quality.json), [summary](reports/summary.json), [environment](reports/environment.json), and [verification](reports/verification.json).

The **Mindweave synthetic** public export contains **300 members, 2,000 check-ins, 3 branches and 5 plans**. Check-ins cover **only 32 members**. The remaining **268 have no exported visits**, which is not evidence of inactivity. **140 members have recorded cancellation dates**, but contractual fields are excluded from attendance feature construction. **48 reported session overlaps** are flagged and retained for investigation.

### Reproduce

For the active monthly research, create/activate the Python environment and install `requirements.txt`, then run:

Full bridge verification also requires the current Retention v0.5 canonical feature export in the sibling lab. The source-only monthly analysis can record that export as unavailable; it cannot claim a verified canonical bridge in that case.

```powershell
python scripts/acquire_berkeley.py --source ../ogdt-retention/data/raw/berkeley/data.zip
python scripts/analyze_berkeley.py
python scripts/execute_notebooks.py --notebook 07_berkeley_monthly_eda.ipynb
python scripts/verify_berkeley.py
```

The source argument can point to another local copy of the official author archive; exact pinned hashes are required. The default uses the already acquired Retention source without modifying that lab. Raw data and person-level derivatives remain local, ignored by Git. The published sample is not reproduced; regular contract months use an explicitly documented conservative policy. The author archive's redistribution terms remain pending review. Shared source identity permits only namespaced member/month joins. Retention v0.5 now has its own historical target/benchmark; this lab imports neither outcomes nor scores. Daily metrics cannot be fabricated from these counts.

The following commands rebuild the **preserved synthetic sandbox**:

Python 3.14. See `reports/environment.json` for the exact tested interpreter and package versions. Commands below run from this repository root.

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python src/data/download.py
python scripts/analyze.py
python scripts/build_notebooks.py
python scripts/analyze_longitudinal.py
python scripts/execute_notebooks.py
python -m unittest discover -s tests -v
python scripts/verify.py
```

Downloading the synthetic source requires network access; other steps run offline. Synthetic acquisition is pinned to revision `3ff8e2fd4b429b5d0d4faf79344b3c23bc00fe5e`. The manifest preserves acquisition time, source URLs, byte sizes, and SHA-256 hashes; analysis verifies hashes before loading. AppleDouble `._*` metadata files are excluded; all four substantive public data tables are loaded. Raw/derived CSVs and large rendered artifacts are kept locally and ignored by Git; source scripts rebuild them. Do not replace a source revision silently.

### Repository

```text
data/raw/                   Original CSVs, dataset card and source manifest
data/processed/             Candidate metrics, timelines, panels and summaries
notebooks/                  01–03 + 03b synthetic; 07 Berkeley monthly; 04–06 deferred
src/data/                   Acquisition, loading, integrity audits
src/features/               As-of attendance metrics
src/behavior/               Reserved for later validated states
src/segmentation/           Reserved for later interpretable segmentation
src/visualization/          Descriptive plots
scripts/                    Rebuild, notebook execution and verification
tests/                      Meaningful temporal/coverage regression checks
docs/                       Architecture, dictionary, methodology and limits
reports/figures/             11 synthetic-sample PNG figures
reports/longitudinal/        24 historical cutoffs, diagnostics and 5 new figures
reports/berkeley/            Active real monthly research, source audit and 5 figures
handoff/                    Reusable Member Behavior Module interface
```

### Interpretation and next phase

The active Berkeley source contains 491,506 calendar rows and 10,241 IDs. The main policy selects 84,251 regular contract months from 8,073 members, not the published 7,752-member sample. Missing/excluded months break feature windows. Source flags and documented spans define retrospective eligibility; no ingestion clock verifies operational availability. The final 20 October review matched all 81,927 Retention v0.5 feature keys/current counts; our additional 2,324 rows are excluded there by family observed to date. History policies also differ, so features cannot automatically replace its model inputs. No Retention outcomes/scores are joined. See [monthly methodology](docs/monthly_methodology.md) and [bridge evidence](reports/berkeley/integration_readiness.json).

On 18 October 2026 the Observe extension added historical member snapshots, within-member 30-day count changes, matched-cohort window sensitivity, feature diagnostics and explicit acquisition-readiness evidence. It uses only pre-cutoff events at each date and preserves unknown sample attendance. This advances descriptive longitudinal EDA; verified capture, timezone and access context remain unmet prerequisites for state calibration. See [the extension report](reports/longitudinal/report.md) and the headers-only [capture template](handoff/observation_coverage_template.csv). The original milestone report remains unchanged.

Candidate attendance metrics have `coverage_verified=false`. A numeric zero means no exported event in that period; it cannot establish dormant behavior. The reference cutoff is **2024-12-29 00:00 exclusive**, in the unspecified source clock, not the analysis date. Calendar opportunity is not entitlement or capture completeness. No visit counts should be used as final engagement thresholds.

Phase 2 should first establish complete acquisition coverage and exposure, then examine recency/frequency/trend/consistency distributions and longitudinal stability. See [proposed state research](docs/behavioral_state_definition.md). Any later segmentation must change a concrete operational decision. Behavioral risk must never be presented as churn probability without independently validated contractual outcomes.

The secondary Kaggle dataset `sharanshetty79/gym-membership-prediction` is deferred. It may independently test concepts or methods; it must never be merged row by row with this source.

### Source, attribution and portfolio framing

Active source: [Berkeley author replication archive — Paying Not to Go to the Gym](https://eml.berkeley.edu/~sdellavi/data/gymdata.shtml), DellaVigna and Malmendier, AER 2006. Real historical fitness records, monthly public source table. See the recorded suitability/selection decisions and pending redistribution terms. This is not a validation in present-day gyms.

[Gym & Fitness Club Membership Dataset — Mindweave Technologies / Hugging Face](https://huggingface.co/datasets/mindweave/gym-memberships), **synthetic public free sample**, licensed [CC-BY-NC-4.0](https://creativecommons.org/licenses/by-nc/4.0/). Preserve provider attribution and non-commercial restrictions when redistributing source data or derivatives. The provider's advertised full dataset is outside this milestone; no purchase was made.

Portfolio message: “I developed a longitudinal framework for converting gym attendance events into member engagement states and behavioral risk signals.” At this milestone, qualify it as the **observation and candidate-metric foundation**; states and risk signals remain future validated outputs. Project title: **Gym Member Behavior & Engagement Intelligence**.
