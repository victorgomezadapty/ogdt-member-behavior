# Berkeley monthly adapter — definitions and limits

The source decision precedes the pipeline and is recorded in the [plan](project_plan.md) and the [suitability review](data_readiness.md). This research uses real historical gym records, separate from the synthetic sandbox. No models are trained and no contractual outcomes are adjudicated.

## Grain, key and identity

One source row is one ID and month. The canonical key is `(dataset_id, member_id, period_end)`, with `dataset_id=berkeley_gym_aer_2006`, `member_id=str(int(id))` and `period_end` as the last calendar day of the MATLAB month `time`. `as_of_exclusive` is midnight on the day after `period_end`; it is not a visit timestamp or a verified ingestion time.

The source has 491,506 calendar rows and 10,241 IDs; many months are padding without a contract. An eligibility table keeps every key; the metrics table contains only eligible months. A missing value after a left join with Retention means **monthly metric not available under this policy**, never zero attendance. Keys and hashes verify population identity, but they do not make two selection policies equivalent.

## Conservative regular-month policy

Require at the same time `contract in {1,2}`, `duplicate=0`, `problem=0`, `overtime=0`, `time >= begatt`, `time <= endatt`, and a month within April 1997–July 2000 for club 11 or April 1997–February 2001 for clubs 13 and 16. The flags are the authors'; a duplicate flag does not mean a duplicated `(id,time)`. Their original rows are never silently dropped: they stay audited, with null analytical attendance.

Prorated codes, promotions, transitions, freezes, non-payment and months without a contract are left out of the main analysis. Not all spells or family exclusions are reconstructed, so this does not reproduce the paper's sample. The selection favors regular months and changes the sample's composition and follow-up. Comparisons by contract type are descriptive and do not identify causal effects.

The file contains club 11 attendance in August 2000 even though `overtime=1`. Its explicit exclusion and the published period take precedence; positive attendance does not establish eligibility. A zero in an eligible month is kept as a recorded count; it does not prove absolute absence or a Dormant state.

## Metrics and windows

The catalog [monthly_feature_catalog.csv](../handoff/monthly_feature_catalog.csv) defines every field with its meaning, requirements, window and limitations. All windows contain the current and previous months; none uses future months. They require calendar consecutiveness and eligibility in every month needed. A gap, an excluding flag or a non-regular month breaks the history. Windows are never extended over the next valid month.

- `recorded_attendance_month`: `attend` for the eligible month, in recorded visits.
- `attendance_previous_month`: count for the immediately preceding calendar month, only if both months are eligible and consecutive.
- `attendance_change_vs_previous_month`: current − previous. A negative sign is not a validated disengagement state.
- `attendance_pct_change_vs_previous_month`: current/previous − 1; null if the previous month is missing or its count is 0.
- `attendance_sum_3_calendar_months` / `attendance_mean_3_calendar_months`: sum over three consecutive eligible months and that sum/3. It is not `visits_90d`.
- `attendance_std_3_calendar_months`: population standard deviation (`ddof=0`) of those three counts; 0 for three zeros does not mean a stable habit.
- `positive_attendance_months_3`: number of months with a count >0 in the same complete three-month window; range 0–3. It is not weekly frequency or active weeks.
- `attendance_sum_6_calendar_months` / `attendance_mean_6_calendar_months`: sum and mean over six consecutive eligible months. Null if any month is missing.
- `consecutive_eligible_months`: length of the observed eligible run ending in the current month. It is not contract tenure or a join date.
- `months_since_recorded_positive_month`: distance in calendar months to the last month with a count >0 within the current eligible run. The current positive month is 0. If the run contains only zeros it is null: the last positive month before the edge or gap is unknown. It is not visit recency in days.

No daily 7/30/90-day metrics, day or hour preferences, cross-branch visits or individual cancellations are computed from this monthly aggregate. Missing detail is never invented.

## Eligibility audit

`member_month_eligibility.csv` keeps the three key fields, the club and `source_contract_code` as context. `excluded_outside_documented_span`, `excluded_author_duplicate`, `excluded_author_problem`, `excluded_overtime` and `excluded_nonregular_contract` are flags that can overlap. `attendance_eligible` is the conjunction of their negations. `eligibility_status` describes that decision; `recorded_attendance_month` is null in every excluded row. These review fields are neither predictors nor behavioral labels.

Sequential exclusion counts show a cascade and must not be added to the overlapping flags. Monthly and per-club summaries include eligible rows, members, sum, mean, median and the fraction of recorded zeros. The histogram and the overall mean weight member-months; they are not equal-weight averages per member. The time chart reflects a changing composition of regular months, not complete gym attendance or validated seasonality.

The six illustrative trajectories are chosen deterministically by total-volume rank among members with at least six eligible months. They are labelled A–F in the chart; ineligible or unavailable months are breaks or nulls, not zeros. They are not a representative sample or engagement states. Because they are per-person series, that figure stays in the local report only and is never published.

## Time, integration and availability

The research assumption is that aggregated attendance is available at month close. There is no ingestion clock, revision history or production availability check. Extract limits and retrospective flags only select and audit; they are excluded from the feature table, together with contract end dates, demographics and prices. Time-correct windows do not remove retrospective selection bias.

The Retention check uses source hashes and the full three-part key. In the final review on 20 October its v0.5 contract and its actual feature export were read: 81,927 shared keys and identical current counts; the 2,324 rows present only here meet its cumulative exclusion of family observed up to t. No people from Mindweave or Lisbon are joined.

Retention represents the close as the last nanosecond of the month; this lab uses the exclusive boundary at the start of the next day. `as_of_exclusive = prediction_date + 1 ns` is verified, and the join uses `period_end`, not those different timestamps. Retention admits prorated history (11/21) inside episodes; our history requires regular months. For 6,964 keys its previous month is available and ours is not; for 6,712 the same holds for its three-month window. When both windows are available, agreement is checked after inverting its log1p. This does not allow replacing its features or model with ours.

Its `berkeley_clear_transition_v1` target and historical benchmark already exist, scoped to clear states and proxy availability. No outcomes, scores or models were imported into Member Behavior. Only keys, counts, feature coverage and boundaries were compared; this bridge does not validate operational results, interventions or engagement states. The integration JSON also pins the hashes of the export and contract that were read.

## Scope of the evidence

These are real historical data from three clubs, with this lab's own regular-month policy. They do not validate behavior in present-day gyms, prediction, latent engagement or a causal benefit of contacting a member. Review publication terms before redistributing original rows or identifiable derivatives. Person-level files are generated locally only and are ignored by Git.
