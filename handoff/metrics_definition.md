# Precise metric definitions

Synthetic sample, exploratory only. The complete per-field dictionary is `feature_catalog.csv`. This defines the calculation conventions shared by the Member Behavior Module.

Let `C` be an exclusive midnight cutoff in the documented event clock. For the demo `C = 2024-12-29 00:00` (source timezone unknown). Count exported events with `C − N days ≤ timestamp < C`. Do not use data on/after C. Do not use today's date or cancellation outcomes to construct attendance metrics.

- **visits_7d / 30d / 90d:** event counts in the corresponding trailing half-open windows; distinct reported events, not unique attendance days.
- **days_since_last_visit:** date(C) minus date(last exported event before C). A visit on C's preceding calendar day produces 1. Null if no known event. This is source-clock calendar recency, not elapsed 24-hour periods.
- **attendance_frequency_30d / 90d:** exported window events divided by N, multiplied by 7; units are nominal events/week. Null if tenure < N. This demo does not adjust for access entitlement or verified capture.
- **visits_previous30d:** count in `[C − 60 days, C − 30 days)`.
- **attendance_change_30_vs_previous30:** current 30-day count minus previous 30-day count; null if tenure < 60 days. Difference in event counts, not probability.
- **attendance_pct_change_30_vs_previous30:** `current / previous − 1`; null for previous = 0 or insufficient tenure. No fabricated infinite increase.
- **attendance_change_30_vs_90_baseline:** current 30-day count minus `(visits_90d − visits_30d) / 2`. Baseline uses the preceding non-overlapping 60 days as a 30-day equivalent. Null if tenure < 90. This choice avoids a self-inclusive baseline.
- **active_weeks_8w:** count of complete Monday–Sunday weeks with ≥1 exported event, out of eight weeks. End is the Monday at/before C; if C is Monday it ends exactly at C. Start is end − 56 days. Null if signup is after start. Current partial week is excluded.
- **attendance_variability:** population standard deviation (`ddof=0`) of the eight weekly counts, including zero-export weeks; same full-tenure rule. Low variability can describe eight zero-export weeks and cannot imply strong habit.
- **preferred_day / preferred_time:** modal day-name or clock-hour band among trailing 90-day events. Ties join labels alphabetically with `|`. No events gives null. Bands are [00:00,05:00), [05:00,12:00), [12:00,17:00), [17:00,22:00), [22:00,24:00); they have unequal lengths and are not opportunity-adjusted preferences. Support is `preference_visit_support_90d`.
- **membership_tenure_days:** date(C) − signup_date. Signup is a start proxy and tenure does not measure uninterrupted membership.
- **branch_diversity:** number of distinct visited branches in trailing 90 days. Zero with represented lifetime visits means no exported event in this window, not a member who chooses no branch.

**Unknown versus zero:** A roster member with no lifetime exported events before C has `no_visits_in_public_sample`; all numeric attendance features are null, while signup-derived tenure remains available. For a member with exported history, window zero counts describe this export only. Every demo row has `coverage_verified=false`; full-tenure flags indicate calendar opportunity, not full capture. Contract status and cancel dates are not inputs. Features after contract end remain descriptive export summaries and must not be used as outreach eligibility.

**Calendar descriptive exports:** member-week and member-month panels enumerate only represented members from signup within the global observed-date span. Partial periods retain calendar opportunity days and a flag. Zero export periods, including time after recorded cancellation, are not verified inactivity. Monthly density divides exported events by these selected members' calendar days and is not entitlement-adjusted attendance. Day-of-week density divides events by calendar occurrences of each weekday inside the observed span. Tenure-bin counts are event age distributions, not normalized attendance rates.

**Timeline:** signup, first/last exported visit and available recorded cancellation dates are distinct event types. Same first/last visit can produce both boundary markers. No inferred habit/state event is emitted. Contract dates are date-only descriptive markers, not metric labels.

No engagement state, behavioral risk score, habit-strength score, clustering label or churn probability is defined in this milestone. Real deployment requires verified collection coverage, exposure, temporal validation and operational interpretation before those outputs can be offered.

The Observe extension reuses these 29 fields at each historical cutoff. Its six extra snapshot metadata fields, comparison-eligibility masks, diagnostic populations and matched-cohort sensitivity columns are defined in [longitudinal methodology](../docs/longitudinal_methodology.md). Snapshot scheduling follows calendar cutoffs; the 30/90-day metric windows retain fixed durations. Arithmetic sign agreement is a definition-sensitivity diagnostic, not a state or accuracy metric.
