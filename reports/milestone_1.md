# Milestone 1 — Observe Member Behavior

**Gym Member Behavior & Engagement Intelligence · Open Gym Digital Twin**

**All data and results are synthetic. This is a selected public sample, not a real-gym study.**
Source: [Mindweave / Hugging Face](https://huggingface.co/datasets/mindweave/gym-memberships), revision `3ff8e2fd4b429b5d0d4faf79344b3c23bc00fe5e`. Analysis date: 2026-10-13. Data clock: 2023–2024; recency uses the dataset cutoff, never today's date.

## The central result is a coverage constraint

There are **300 roster members**, **2,000 exported check-ins**, **3 branches**, and **5 plans**. Visits cover **32 members (10.7%)**, IDs 1–32. The other **268 members have no check-ins in the export**. Event IDs are 1–2000, consecutive in this revision. This ordering is consistent with a member-ordered excerpt; the provider does not document its sampling mechanism or complete capture. Even ID 32's completeness is unknown. Missing exported records cannot establish inactivity, disengagement, or churn.

## Architecture and time bounds

Four CSV tables loaded and checked: members → plans/home locations; check-ins → members/visited locations. See [entity relationships](../docs/entity_relationships.md) and [dictionary](../docs/data_dictionary.md).

- Signup dates: 2023-01-01 to 2024-12-21.
- Check-ins: 2023-01-12 18:26:00 to 2024-12-28 09:33:00.
- Non-null cancellation dates: 2023-02-01 to 2024-12-28.
- Exclusive feature cutoff: **2024-12-29 00:00:00**, timezone unspecified. The last recorded day may be incomplete.
- Public cancellation data is present: **140 cancel dates**, **140 reasons**, **140 inactive-status rows**. These are contractual snapshot fields. They do not define attendance states and are excluded from feature calculations.
- No class bookings, renewal, expiration, operational closure calendar, anomaly labels, plan history, or per-member extraction completeness fields exist in the public tables.

## Quality audit

All 30 hard integrity checks pass at the pinned revision. No records are silently deleted. Null counts are in the dictionary and `reports/data_quality.json`.

| Check | Count |
| --- | --- |
| members_missing_pk | 0 |
| members_duplicate_pk | 0 |
| members_nonpositive_pk | 0 |
| checkins_missing_pk | 0 |
| checkins_duplicate_pk | 0 |
| checkins_nonpositive_pk | 0 |
| locations_missing_pk | 0 |
| locations_duplicate_pk | 0 |
| locations_nonpositive_pk | 0 |
| plans_missing_pk | 0 |
| plans_duplicate_pk | 0 |
| plans_nonpositive_pk | 0 |
| members_plan_id_missing_or_orphan | 0 |
| members_location_id_missing_or_orphan | 0 |
| checkins_member_id_missing_or_orphan | 0 |
| checkins_location_id_missing_or_orphan | 0 |
| duplicate_event_signature | 0 |
| duplicate_member_timestamp | 0 |
| missing_checkin_timestamp | 0 |
| missing_signup_date | 0 |
| missing_or_nonpositive_duration | 0 |
| missing_or_nonpositive_capacity | 0 |
| missing_or_negative_price | 0 |
| invalid_plan_share | 0 |
| checkin_before_signup | 0 |
| checkin_after_cancel_day | 0 |
| cancel_before_signup | 0 |
| active_with_cancel_date | 0 |
| inactive_without_cancel_date | 0 |
| cancel_reason_without_date | 0 |

Additional observations, retained for review: **252 member-days with multiple visits**, **48 overlapping reported sessions**, **0 visits on cancellation dates**, **0 visits away from the home branch**. Multiple events per day are not deduplicated merely for sharing a day. Overlaps are a plausibility flag; assess real access-log semantics before deployment. Duration spans 15–151 minutes; no undocumented upper threshold is treated as an error.

## Attendance distributions and intervals

Among the 32 members with exported visits, total-event count median is **55.0**, IQR **20.8–89.5**, range **4–176**, mean **62.50**. Totals span different tenure and follow-up windows; they are not comparable engagement labels.

The selected-member calendar panels contain **1855 member-weeks** and **439 member-months** after signup within the observed export span. Median exported counts are **0.0/week** and **4.0/month**; zero-export shares are **52.3%** and **36.7%**. Boundary/signup partial periods are flagged. Periods after a recorded cancellation are retained as calendar context, not counted as entitlement or inactivity evidence.

Median gap between consecutive exported events is **2.42 days** (IQR 0.96–4.97; 1968 intervals). Gaps can reflect sampling and include same-day repeats.

## Day and time

| day | events | observed_calendar_days | events_per_calendar_day |
| --- | --- | --- | --- |
| Monday | 299 | 102 | 2.931 |
| Tuesday | 299 | 102 | 2.931 |
| Wednesday | 302 | 102 | 2.961 |
| Thursday | 277 | 103 | 2.689 |
| Friday | 258 | 103 | 2.505 |
| Saturday | 272 | 103 | 2.641 |
| Sunday | 293 | 102 | 2.873 |

Peak recorded clock hour is **07:00**. All 24 hourly counts are exported. Time bins are display conventions, not behavioral thresholds; unequal bin durations preclude a simple preference comparison without hour adjustment. Weekend figures use Saturday/Sunday for exploratory display only, not a jurisdiction-specific operational calendar.

## Tenure, early behavior, plans, and branches

Tenure is calendar days from signup to event, not continuous active membership duration. Tenure bands are descriptive bins, not engagement rules; follow-up and population exposure are unequal.

| tenure_band | events | members_with_events |
| --- | --- | --- |
| 0–29 | 235 | 31 |
| 30–89 | 387 | 28 |
| 90–179 | 448 | 23 |
| 180–364 | 660 | 16 |
| 365+ | 270 | 8 |

First-30-tenure-day distribution: **31 selected members** have 30 calendar days of opportunity within the export span; median exported count **8.0**, range **0–13**. Calendar opportunity does not verify full event capture or membership entitlement.

| visit_branch | events | members_with_events |
| --- | --- | --- |
| IronFit Downtown | 754 | 14 |
| IronFit Eastside | 575 | 7 |
| IronFit Pearl District | 671 | 11 |

| plan_name | events | members_with_events |
| --- | --- | --- |
| Basic Annual | 419 | 6 |
| Basic Monthly | 293 | 7 |
| Premium Annual | 392 | 5 |
| Premium Monthly | 763 | 12 |
| Student | 133 | 2 |

Plan is a static snapshot and cannot establish the plan held at each historical visit. Raw subgroup counts reflect unequal sample support. Branch differences cannot establish comparative performance.

## Monthly patterns

| month | exported_events | members_with_exported_events | roster_signups | selected_member_calendar_days | events_per_selected_member_calendar_day | boundary_month |
| --- | --- | --- | --- | --- | --- | --- |
| 2023-01 | 12 | 2 | 44 | 34 | 0.3529 | True |
| 2023-02 | 31 | 6 | 16 | 86 | 0.3605 | False |
| 2023-03 | 39 | 8 | 9 | 223 | 0.1749 | False |
| 2023-04 | 30 | 7 | 7 | 240 | 0.125 | False |
| 2023-05 | 62 | 7 | 12 | 248 | 0.25 | False |
| 2023-06 | 56 | 7 | 7 | 240 | 0.2333 | False |
| 2023-07 | 66 | 8 | 8 | 276 | 0.2391 | False |
| 2023-08 | 55 | 7 | 4 | 279 | 0.1971 | False |
| 2023-09 | 56 | 11 | 16 | 357 | 0.1569 | False |
| 2023-10 | 99 | 11 | 13 | 434 | 0.2281 | False |
| 2023-11 | 115 | 13 | 14 | 465 | 0.2473 | False |
| 2023-12 | 97 | 13 | 10 | 496 | 0.1956 | False |
| 2024-01 | 89 | 16 | 38 | 602 | 0.1478 | False |
| 2024-02 | 119 | 17 | 18 | 648 | 0.1836 | False |
| 2024-03 | 142 | 17 | 12 | 738 | 0.1924 | False |
| 2024-04 | 138 | 16 | 4 | 720 | 0.1917 | False |
| 2024-05 | 86 | 15 | 4 | 744 | 0.1156 | False |
| 2024-06 | 117 | 14 | 5 | 734 | 0.1594 | False |
| 2024-07 | 126 | 15 | 4 | 805 | 0.1565 | False |
| 2024-08 | 91 | 12 | 7 | 847 | 0.1074 | False |
| 2024-09 | 96 | 14 | 14 | 851 | 0.1128 | False |
| 2024-10 | 111 | 15 | 13 | 939 | 0.1182 | False |
| 2024-11 | 115 | 14 | 14 | 952 | 0.1208 | False |
| 2024-12 | 52 | 13 | 7 | 896 | 0.058 | True |

The exported visit peak is **2024-03 (142 events)**. The roster contains **82 January signups** across two years. Compare same months across years in Figure 08. The adjusted export-density denominator counts selected members' calendar days since signup inside the observed span; it ignores contract entitlement and is not an attendance rate. The selected population changes with signup, and export completeness is unknown. Do not infer a validated January effect, summer effect, closure, or promotional impact from these totals. Only two synthetic years and no anomaly event dates/branches are available.

## Individual trajectories and member timeline

Figure 09 shows every member with exported visits. Figure 10 selects six members deterministically at evenly spaced attendance-volume ranks, showing signup and available cancellation-date overlays. This exposes trajectory heterogeneity without assigning states. `member_timeline.csv` includes signup, first/last exported visit, and recorded cancellation where available for all roster members. Habit formation, stable attendance, decline, and inactivity are not asserted as timeline events without validated definitions.

## Candidate metrics and real-gym requirements

`member_metrics.csv` contains 300 rows at the dataset cutoff. Members without exported events retain null attendance metrics and `no_visits_in_public_sample`. The 32 other rows have sample-derived candidates, all with `coverage_verified=false`. Recent zero counts in those rows still mean zero exported records, not verified inactivity. Every feature is defined with window, meaning, requirements, and limits in [feature catalog](../handoff/feature_catalog.csv) and [metric definitions](../handoff/metrics_definition.md).

Minimum real-gym inputs: stable member ID and visit timestamp, plus extraction coverage and timezone metadata to interpret absence. Add membership start for tenure, event branch and plan history for context, and closure calendars for exposure. Contractual outcomes belong to the Retention Module. See [data contract](../handoff/data_contract.yaml).

## Limits and proposed Phase 2

Synthetic generation, selected member/event export, undated status snapshots, unspecified timezone, no entitlement/history or acquisition coverage, and unlabelled operational anomalies prevent real-world engagement or churn claims. See [dataset limitations](../docs/dataset_limitations.md).

Phase 2: obtain a dataset with verified member-level event coverage; audit windows and closures; examine recency, frequency, trend and consistency jointly with tenure-aware denominators; compare same-member trajectories; calibrate candidate thresholds against distributions and operational review; assess temporal stability before state definitions. Only then consider interpretable segmentation tied to specific decisions. A later secondary dataset should test methods independently, never row-merge unrelated people. Behavioral risk is not churn probability. No ML, final states, clusters, risk scores, or churn model were produced in Milestone 1.

## Figures

### Coverage comes before engagement interpretation

![Coverage comes before engagement interpretation](figures/01_coverage_and_volume.png)

### Visit timeline: observed export, January 2023–December 2024

![Visit timeline: observed export, January 2023–December 2024](figures/02_visit_timeline.png)

### Volume distributions include zero-export periods after signup

![Volume distributions include zero-export periods after signup](figures/03_week_month_distributions.png)

### Day of week: raw counts and calendar-day adjustment

![Day of week: raw counts and calendar-day adjustment](figures/04_day_preference.png)

### Time of day: preserve the source clock

![Time of day: preserve the source clock](figures/05_time_preference.png)

### Tenure describes event age, with unequal follow-up

![Tenure describes event age, with unequal follow-up](figures/06_membership_tenure.png)

### Branch and plan comparisons reflect selected members

![Branch and plan comparisons reflect selected members](figures/07_branch_and_plan.png)

### Month-of-year attendance and signup patterns

![Month-of-year attendance and signup patterns](figures/08_monthly_patterns.png)

### Individual histories: 32 members with at least one exported visit

![Individual histories: 32 members with at least one exported visit](figures/09_member_month_heatmap.png)

### Six trajectories: monthly totals anchored at period end

![Six trajectories: monthly totals anchored at period end](figures/10_individual_trajectories.png)

### Early attendance and gaps remain sample-dependent

![Early attendance and gaps remain sample-dependent](figures/11_early_behavior_and_gaps.png)
