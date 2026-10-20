# Longitudinal attendance exploration — Observe extension

**Gym Member Behavior & Engagement Intelligence · 18 October 2026**

**Synthetic selected public sample. Capture remains unverified. No states, thresholds, segmentation, risk scores or churn model are produced.** This extends the observation milestone with repeated historical summaries; it does not satisfy the completeness gates for state calibration. The source revision and raw files are unchanged from Milestone 1.

## What changed

Reconstructed **24 exclusive cutoffs**, from **2023-02-01** through **2024-12-29**, yielding **4,197 member-snapshot rows**. Calendar month-end snapshots use the next month's midnight; the final 2024-12-29 cutoff is explicitly a partial-month boundary. Metrics retain fixed trailing 7/30/90-day windows, not calendar-month counts. Each snapshot includes only roster members signed up and exported events strictly before that cutoff. Later events cannot turn an earlier unknown member into a represented member. The roster itself is a retrospective snapshot, so event-time filtering is not a claim of historical data availability: ingestion timestamps and backfill history are absent.

## Support before interpretation

At the final cutoff: 300 signed-up roster rows, 32 members with exported history, 268 with no exported history, and **0 with verified capture**. Calendar eligibility requires exported history, sufficient signup age and a nominal window inside the earliest pre-cutoff exported date. This is a conservative span check, not evidence of acquisition completeness or entitlement.

| as_of_exclusive | signed_up_roster | members_with_exported_history | calendar_eligible_30d | calendar_eligible_60d | calendar_eligible_90d |
| --- | --- | --- | --- | --- | --- |
| 2023-02-01 00:00:00 | 44 | 2 | 0 | 0 | 0 |
| 2023-03-01 00:00:00 | 60 | 6 | 2 | 0 | 0 |
| 2023-04-01 00:00:00 | 69 | 8 | 7 | 2 | 0 |
| 2023-05-01 00:00:00 | 76 | 8 | 8 | 7 | 2 |
| 2023-06-01 00:00:00 | 88 | 8 | 8 | 8 | 7 |
| 2023-07-01 00:00:00 | 95 | 8 | 8 | 8 | 8 |
| 2023-08-01 00:00:00 | 103 | 9 | 8 | 8 | 8 |
| 2023-09-01 00:00:00 | 107 | 9 | 9 | 8 | 8 |
| 2023-10-01 00:00:00 | 123 | 14 | 9 | 9 | 8 |
| 2023-11-01 00:00:00 | 136 | 14 | 14 | 10 | 9 |
| 2023-12-01 00:00:00 | 150 | 16 | 14 | 14 | 10 |
| 2024-01-01 00:00:00 | 160 | 16 | 16 | 14 | 14 |
| 2024-02-01 00:00:00 | 198 | 21 | 17 | 16 | 14 |
| 2024-03-01 00:00:00 | 216 | 23 | 22 | 17 | 16 |
| 2024-04-01 00:00:00 | 228 | 24 | 23 | 22 | 17 |
| 2024-05-01 00:00:00 | 232 | 24 | 24 | 23 | 22 |
| 2024-06-01 00:00:00 | 236 | 24 | 24 | 24 | 23 |
| 2024-07-01 00:00:00 | 241 | 25 | 24 | 24 | 24 |
| 2024-08-01 00:00:00 | 245 | 26 | 26 | 24 | 24 |
| 2024-09-01 00:00:00 | 252 | 28 | 26 | 26 | 24 |
| 2024-10-01 00:00:00 | 266 | 28 | 28 | 26 | 26 |
| 2024-11-01 00:00:00 | 279 | 31 | 29 | 28 | 26 |
| 2024-12-01 00:00:00 | 293 | 32 | 31 | 29 | 28 |
| 2024-12-29 00:00:00 | 300 | 32 | 32 | 31 | 29 |

## Within-member count changes

The final 60-day calendar-eligible cohort contains **31 members**. Current-minus-previous 30-day exported counts are positive for **2**, equal for **20**, and negative for **9**. These are arithmetic count comparisons. Equality does not establish Stable; a negative difference does not establish Declining; zeros do not establish Dormant. Cancelled memberships remain in these descriptive export summaries; entitlement is not inferred and outreach eligibility is not produced.

An illustration selected deterministically from the smallest non-zero current count shared by members with different changes:

| member_id | visits_30d | visits_previous30d | attendance_change_30_vs_previous30 |
| --- | --- | --- | --- |
| 1 | 1.0 | 12.0 | -11.0 |
| 15 | 1.0 | 9.0 | -8.0 |

This illustrates information lost by current volume alone, without asserting engagement or causal explanations. The heatmap shows changes at each historical cutoff; gray cells are unavailable comparisons.

## Window and baseline sensitivity

The matched cohort with 90 days of calendar opportunity contains **29 members**. Comparing the sign of current30 − previous30 with current30 − preceding60/2 yields **4 disagreements (13.8%)**. Zero is treated as a distinct arithmetic sign. Disagreement is definition sensitivity, not misclassification against ground truth. The 90-day rate includes the latest 30 days and is therefore statistically dependent on the 30-day rate; their comparison is descriptive, not an independent validation. No thresholds are selected from these small synthetic distributions.

## Feature diagnostics

All roster nulls and represented-row summaries are shown separately. Zero fraction uses non-null represented rows; missing members are never filled with zero. Quantiles and distinct counts are descriptive diagnostics, not engagement thresholds.

| feature | roster_rows | represented_members | non_null_roster | non_null_represented | null_fraction_roster | distinct_values_represented | zero_fraction_of_nonnull_represented | p25 | median | p75 | minimum | maximum |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| visits_7d | 300 | 32 | 32 | 32 | 0.893 | 2 | 0.938 | 0.0 | 0.0 | 0.0 | 0.0 | 1.0 |
| visits_30d | 300 | 32 | 32 | 32 | 0.893 | 9 | 0.594 | 0.0 | 0.0 | 2.0 | 0.0 | 11.0 |
| visits_90d | 300 | 32 | 32 | 32 | 0.893 | 11 | 0.5 | 0.0 | 2.0 | 17.5 | 0.0 | 35.0 |
| days_since_last_visit | 300 | 32 | 32 | 32 | 0.893 | 30 | 0.0 | 23.75 | 85.5 | 264.25 | 1.0 | 652.0 |
| attendance_frequency_30d | 300 | 32 | 32 | 32 | 0.893 | 9 | 0.594 | 0.0 | 0.0 | 0.467 | 0.0 | 2.567 |
| attendance_frequency_90d | 300 | 32 | 29 | 29 | 0.903 | 10 | 0.552 | 0.0 | 0.0 | 1.322 | 0.0 | 2.722 |
| attendance_change_30_vs_previous30 | 300 | 32 | 31 | 31 | 0.897 | 9 | 0.645 | -3.0 | 0.0 | 0.0 | -11.0 | 3.0 |
| attendance_pct_change_30_vs_previous30 | 300 | 32 | 13 | 13 | 0.957 | 11 | 0.154 | -0.889 | -0.714 | 0.0 | -1.0 | 0.429 |
| attendance_change_30_vs_90_baseline | 300 | 32 | 29 | 29 | 0.903 | 12 | 0.552 | -3.5 | 0.0 | 0.0 | -11.0 | 5.5 |
| active_weeks_8w | 300 | 32 | 31 | 31 | 0.897 | 7 | 0.548 | 0.0 | 0.0 | 5.0 | 0.0 | 8.0 |
| attendance_variability | 300 | 32 | 31 | 31 | 0.897 | 14 | 0.548 | 0.0 | 0.0 | 1.209 | 0.0 | 1.965 |
| branch_diversity | 300 | 32 | 32 | 32 | 0.893 | 2 | 0.5 | 0.0 | 0.5 | 1.0 | 0.0 | 1.0 |

Branch diversity is structurally limited in this source: it counts distinct exported branches, and the inspected events never leave members' home branches. A low-information feature in this sample may still be useful in a real chain with verified multi-branch visits. Low variability across zero-export weeks does not establish a stable habit.

## Readiness and next work

Three input requirements remain unmet: verified member-level capture intervals; source timezone; effective access and operating calendars. See [readiness evidence](readiness.json) and [input template](../../handoff/observation_coverage_template.csv). The empty template contains column headers only, not invented coverage rows. Source cancellation fields cannot fill these acquisition gaps. Obtaining those fields is the next gate before state/threshold calibration. Meanwhile the code can reproduce descriptive historical metrics and test temporal filtering.

The secondary Kaggle dataset remains deferred and is not merged with this source. No purchase, external publication or real-member outreach is part of this work. The methodological findings are transferable; the numerical values are synthetic and sample-specific. Snapshot rows are repeated measures, not independent members; no significance tests, prediction performance or real-gym generalization is claimed.

## Reproduction and output contract

Run `python scripts/analyze_longitudinal.py`, then execute the generated `03b_longitudinal_eda.ipynb`. Outputs are under `data/processed/longitudinal/`. [Schema and definitions](../../docs/longitudinal_methodology.md) cover the existing 29 metric fields and six new snapshot metadata fields. The original [Milestone 1 report](../milestone_1.md) remains available.

## Figures

### Historical support grows with signup and exported history

![Historical support grows with signup and exported history](figures/01_snapshot_support.png)

### Within-member count changes vary across historical cutoffs

![Within-member count changes vary across historical cutoffs](figures/02_member_change_panel.png)

### Joint metrics expose why one attendance count is insufficient

![Joint metrics expose why one attendance count is insufficient](figures/03_joint_metrics.png)

### Baseline and window choices change the descriptive signal

![Baseline and window choices change the descriptive signal](figures/04_window_sensitivity.png)

### Feature availability and variation limit interpretation

![Feature availability and variation limit interpretation](figures/05_feature_support.png)
