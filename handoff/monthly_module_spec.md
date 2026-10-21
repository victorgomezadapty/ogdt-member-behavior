# Monthly Member Behavior · component specification

Purpose: turn eligible monthly attendance into 12 descriptive metrics with explicit support and nulls.
Input: the exact Berkeley source, with verified ZIP and table hashes and schema; unique id/time keys;
selection `berkeley_regular_month_v1`. Output: one row per eligible `(dataset_id,member_id,period_end)`,
12 metrics and metadata defined in the [catalog](monthly_feature_catalog.csv). It produces no outcomes or states.

Active handoff: `monthly_data_contract.yaml`, `monthly_feature_catalog.csv`,
`monthly_metrics_definition.md`, `monthly_findings.md`, `monthly_limitations.md` and this document.
The original synthetic-event handoff is preserved and independent.

Lab implementation: `src/data/berkeley.py`, `src/features/monthly.py`; numpy and pandas.
Verification: `scripts/verify_berkeley.py`; tests in `tests/test_monthly.py`.
Portable notebook: `publication/kaggle/ogdt_monthly_behavior.ipynb`, built from the same functions
without repository imports, precomputed reports or Retention; it runs on Kaggle with the bundled dependencies.

Core adapter: `open-gym-digital-twin/ogdt_core/behavior.py`, standard library only, without importing the lab.
It reads a hash-reviewed export, verifies schema, identity, policy, close and nulls, and recomputes the 12
formulas for every row. `MemberMonthBehavior` uses its own population namespace
`behavior_regular_member_months_v1`. Source, version and full keys are preserved. The optional bridge
to Retention declares the mapping between those two reviewed policies explicitly, checks every key
and current count, and returns aggregate evidence only; it does not mix outcomes or replace features.

Failures: abort on a changed hash, duplicate, unreviewed field, incompatible source or policy, non-calendar
month, non-finite or non-integral current value, wrong clock, or a mismatched formula or null. A change
requires a deliberate manifest review. A missing month breaks windows; it does not create a zero row.
The cut-off is the proxy available close date ≤ as-of; the core exposes only aggregates per metric and month.

Acceptable scope: descriptive historical research, not operations or prediction. Candidate metrics
are not validated engagement states, decisions or risks. The Retention pipeline stays intact.
