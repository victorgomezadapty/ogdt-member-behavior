# Dataset limitations

All analyses use **synthetic data** from the [public Mindweave dataset](https://huggingface.co/datasets/mindweave/gym-memberships). The source card is preserved at the pinned revision in `data/raw/dataset_card.md`. This sandbox cannot establish generalization to real gyms, causal effects, or model performance on real members.

## Public scope and selection

The inspected CSVs contain 300 members, 2,000 check-ins, 3 locations and 5 plans. Check-ins cover only member IDs 1–32. IDs 33–300 have no exported visits; their attendance is **unknown**, not zero. All event capture is unverified, including the 32 represented members. Consecutive event IDs and member ordering suggest a selected excerpt; this is an inference, not a documented extraction design. The last represented member may be truncated, but that cannot be proven from the sample.

The provider's card advertises a larger paid dataset and describes counts inconsistently (2,500 members in prose versus 2,700 in its full-table listing). Neither count is the inspected roster. Do not claim findings for the full source population or purchase/download non-public data as part of this milestone.

## What is actually public

`cancel_date`, `cancel_reason`, and `is_active` are present. 140 member rows have cancellation dates/reasons; 160 active-status rows lack both. Structural nulls are reported, not imputed. This confirms outcome fields exist; it does **not** validate a churn model, the status snapshot date, ongoing membership coverage, complete longitudinal outcomes, or real-world applicability. Contract fields belong to a separate Retention Module and are unused in attendance feature construction.

No public class-booking, renewal, expiration, plan-history, observation-coverage or operational-event tables exist. Source descriptions and tags are not proof of field availability; actual downloaded headers determine the contract.

## Operational anomalies and quality flags

The provider describes a renovation closure and a viral promotional signup spike. Public files include no anomaly identifiers, affected locations, dates, closure hours or ground-truth labels. These events are **documented in general, not identifiable/validated** in this excerpt. Do not label a plotted dip as a closure or a spike as promotion impact without an external calendar.

All 30 hard integrity checks pass, but 48 reported sessions overlap another prior session for the same member. These are plausibility flags retained in the data, not proven fraud or a documented injected anomaly. There are 252 member-days with multiple events. Distinct event IDs are preserved. Source duration may represent a generated session length, not reliable access occupancy or exercise time.

## Time, exposure and comparisons

- Timestamps are naive; source timezone, UTC conversion and daylight-saving semantics are unspecified. Preserve the source clock. The user's Riyadh timezone must not be imposed on these data.
- The first/last observed events do not establish data collection boundaries. The last day and first/last month can be incomplete. Recency is calculated at a dataset-relative exclusive cutoff, not in 2026.
- Signup date is a tenure proxy. It does not establish uninterrupted entitlement, pauses, migrations, reactivation, or access rights. Static plan/home branch is not historical assignment.
- Member-week/month panels include calendar time after signup through the global export span. Zero counts and post-cancellation periods are calendar context, not verified zero eligible attendance. The CSVs flag partial calendar periods and unverified coverage.
- Time-of-day bins have unequal duration; modal bins reflect count concentration, not preference adjusted for opportunity. Preferred days/bins can be ties or low-support estimates.
- Two synthetic years, changing selected-member composition and incomplete acquisition prevent validated seasonality or branch/plan performance conclusions. Calendar-day adjustment does not solve member exposure or sample selection.
- Same-day repeat visits and missing exported events affect inter-visit intervals, volume and consistency. No arbitrary duration cutoff, behavioral threshold or smoothing choice is presented as ground truth.

## Conceptual limits

Attendance cannot measure satisfaction, motivation, exercise quality, health benefit, unrecorded exercise, intent to cancel, or the effect of contacting a member. Attendance decline is a possible behavioral signal; it does not prove contractual churn. Behavioral engagement states, habit-strength proxies and risk scores need explicit validation, uncertainty and operational interpretation. Synthetic cancellation fields do not remove these limits.

Phase 2 should prioritize acquisition completeness, source timezone, entitlement history and operational calendars before state calibration. The secondary Kaggle source remains deferred and must be analyzed independently, never joined as if its people matched these members.
