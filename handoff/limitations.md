# Member Behavior Module limitations

Active real-data research uses the Berkeley monthly panel; see [suitability](../docs/data_readiness.md) and [monthly methodology](../docs/monthly_methodology.md). The regular-month subset is historical, selected and different from the published sample. Calendar-month counts cannot reconstruct daily attendance, visit timestamps, day/time preferences or contractual tenure. Retrospective source flags/endpoints do not provide an ingestion clock. Validated engagement states and operational use remain unresolved; source redistribution terms require review before publication. Retention v0.5 already has its own restricted historical target/benchmark; our final audit compares only its canonical feature keys/counts/boundaries, with no outcomes/scores imported. Family exclusions and prior prorated-month policy differ, so our inputs cannot replace its model features. No cross-population person join is allowed.

The following limitations refer to the preserved synthetic event sandbox:

The demo is a **synthetic selected public sample**; all 300 feature rows carry `coverage_verified=false`. Only 32 members have exported attendance; absence for 268 cannot establish inactivity. The public cancellation fields exist but do not validate churn prediction. The undated `is_active` snapshot cannot label historical engagement.

Attendance signals cannot establish satisfaction, intent, health outcomes, off-site activity, habit, contractual retention or causal intervention effects. Timezone, event capture and operational exposure must be documented. Signup is a tenure proxy; static plans and branches are not effective-dated histories. Zero-export windows and 48 reported overlapping sessions need interpretation before operational use. Two synthetic years and unlabelled closure/promotion events do not establish real seasonality or anomaly detection performance.

The module currently exports descriptive candidate metrics, not calibrated states, segments or risk scores. Behavioral risk would describe potential disengagement, not cancellation probability. Keep Retention Module inputs/outcomes separate and validate any eventual linkage.

Full source-specific discussion: [dataset limitations](../docs/dataset_limitations.md). Exact calculation limitations: [feature catalog](feature_catalog.csv) and [metric definitions](metrics_definition.md). Improve coverage, timezone, entitlement history and operating calendars before Phase 2 state calibration.
