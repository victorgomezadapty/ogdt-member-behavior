# Member Behavior Module — v0.1 Observe

## Active source and monthly interface — 19 October 2026

The active research source is now the real Berkeley monthly fitness panel, following the recorded [source plan](../docs/project_plan.md) and [suitability assessment](../docs/data_readiness.md). The [monthly contract](monthly_data_contract.yaml) and [monthly catalog](monthly_feature_catalog.csv) define the current real-data adapter; the event contract below remains the preserved Mindweave synthetic sandbox interface.

The monthly adapter selects 84,251 regular member-months from 8,073 members under `berkeley_regular_month_v1`. It exposes recorded monthly volume, adjacent changes, complete three/six-calendar-month windows, monthly variability, evidence run length and a monthly positive-attendance recency proxy. This is not a reproduction of the published 7,752-member sample. Excluded or missing months break windows and remain unavailable, not zero. Daily recency, day/time preference and event-level branch diversity cannot be obtained from this aggregate.

Retention shares the exact source-table identity. The final 20 October review inspected v0.5 and matched all 81,927 canonical feature keys/counts; our additional 2,324 rows are explained by its family-as-of exclusion. Integration requires `(dataset_id, member_id, period_end)` plus matching source/export hashes. Its prior prorated-month history differs from our regular-only windows, so inputs cannot be substituted in its model. Retention already has its own historical target/benchmark; this lab imports no outcomes/scores or models. Validated engagement states and operational use remain deferred. Synthetic reports below stay separate and are not evidence of real-member prediction. See [real monthly report](../reports/berkeley/report.md).

**Gym Member Behavior & Engagement Intelligence**, a research module of Open Gym Digital Twin. Milestone 1 is a synthetic-data observation and candidate-feature foundation. The eventual product should understand member state, not only attendance count. This version does not claim to deliver validated states or risk.

## Purpose and boundary

Convert documented attendance events into longitudinal observations of recency, frequency, trend, consistency, tenure and visit preferences. Distinguish observable attendance from interpreted engagement and behavioral disengagement. Contractual retention/cancellation/renewal belongs to the Retention Module; cancellation snapshots are not attendance labels.

## Capabilities by input availability

| Available input | Feasible capability | Required caveat |
| --- | --- | --- |
| member_id + visit_timestamp | Counts, exported recency, gaps, within-member trend, event-day/time patterns | Missing events mean unknown unless capture is verified; no roster means non-attenders cannot be enumerated |
| + roster, timezone and verified capture windows | Distinguish verified zero observations from unavailable periods | Still requires entitlement/closures for access opportunity |
| + membership_start | Tenure-aware and early-membership summaries | Signup may only proxy effective start |
| + event branch and plan/branch history | Contextual comparison and branch diversity | Static snapshots cannot reconstruct history |
| + entitlement and operational calendars | Exposure-adjusted comparisons and event-context review | Validate definitions and capture first |
| + cancellation / renewal / expiration | Join to a separate Retention Module's event ledger | Not a churn model or behavior-state label in this module |

## Current implementation

Input source: four pinned synthetic public CSVs. Load with hashes; audit keys, relations, dates/nulls/duplicates/impossible values; preserve review flags. Use validated joins and a 300-member roster spine. Export one candidate-metric row per member at the exclusive cutoff. Members without exported events retain null attendance metrics; all rows declare unverified capture. Contract/contact fields are excluded from feature calculations. Reproducible functions live in `src/data/load.py` and `src/features/attendance.py`.

Outputs: enriched event table, 300-member metrics, member timeline, selected-member week/month panels, monthly/day/hour/tenure/branch/plan summaries, data-quality audit, 11 figures, three executed notebooks and the report. Data contract and feature catalog document every current interface field. No production endpoint, automatic outreach, ML, segment or state is implemented.

The 18 October 2026 Observe extension adds 24 historical cutoffs, a fourth executed observation notebook, five additional figures, feature support diagnostics and matched-cohort baseline/window sensitivity. Existing metric definitions are unchanged; six snapshot metadata fields are defined in [longitudinal methodology](../docs/longitudinal_methodology.md). Readiness evidence records unmet member capture, timezone and effective-access/operating-context requirements. This is descriptive longitudinal exploration, not state-calibration readiness. A headers-only capture template is provided for future acquisition.

## Future member-state object

Potential outputs include member_recency, member_frequency, member_consistency, attendance_trend, engagement_state, behavioral_risk_score, habit_strength_proxy, preferred_visit_window and member_activity_segment. They are future capabilities, not current field aliases promised to consumers. Validate state definitions using recency/frequency/trend/consistency and explicit availability/uncertainty. A member with 20→12 visits can be declining while 2→4 can be improving; equal current counts do not imply equal state.

## Phase 2 acceptance gates

1. Establish member-specific acquisition completeness, source timezone, event semantics, access history and closure calendars.
2. Audit observation windows and inspect distributions and within-member trajectories by tenure and context.
3. Calibrate candidate rules with operational review and sensitivity/temporal stability checks; specify unavailable/uncertain states and precedence.
4. Explore segmentation only when each group changes a stated operational decision. No clustering for its own sake.
5. Validate behavioral signals separately from contractual outcomes. Churn probability requires appropriate real outcomes and temporal validation in the Retention Lab.
6. Test methods independently on a secondary structure if useful; never row-merge unrelated dataset members.

The provisional data contract records unmet requirements. Synthetic findings can guide methodology and implementation but cannot establish real-member intervention effects or readiness for operational use.
