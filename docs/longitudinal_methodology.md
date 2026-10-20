# Longitudinal attendance exploration — output definitions

This is an **Observe extension**, using the unchanged synthetic public sample. It advances longitudinal EDA while leaving member-state calibration, segmentation and behavioral risk deferred. It does not assert the missing capture requirements have been met.

## Historical snapshots

`src/features/longitudinal.py` reconstructs one row per member per exclusive cutoff. Regular cutoffs are first-of-month midnights, describing the preceding calendar month end. The midnight after the last recorded date is added and labelled as a partial-month boundary if needed. Events strictly on/after a cutoff are excluded. Members whose signup is on/after that cutoff are absent from that snapshot. A member with only future events remains `no_visits_in_public_sample` until their first exported event is before the cutoff. The retrospective roster has no ingestion/effective-history versioning: event-time filtering does not establish historically available production data.

The 29 existing fields retain their definitions from [feature catalog](../handoff/feature_catalog.csv). New metadata in `data/processed/longitudinal/member_snapshots.csv`:

Cutoff dates follow the calendar, but visits_7d/30d/90d remain fixed-length rolling windows; a 30-day count is not necessarily the preceding calendar month's count.

| Field | Definition and business meaning | Window / requirements | Limitations |
| --- | --- | --- | --- |
| export_span_start_as_of | Earliest pre-cutoff exported event date; diagnostic lower bound only | All exported check-ins strictly before C | Global selected export span; not acquisition start or per-member complete capture |
| window_inside_export_span_30d | C−30 days is on/after that diagnostic start | Source-clock dates and C | Does not establish verified capture, access or event completeness |
| window_inside_export_span_60d | Same test for C−60 days | Source-clock dates and C | Same limitations; only calendar comparison support |
| window_inside_export_span_90d | Same test for C−90 days | Source-clock dates and C | Same limitations; only calendar comparison support |
| consistency_inside_export_span | Start of eight complete weeks is on/after diagnostic start | Existing consistency_window_start and pre-C export span | No member-specific acquisition validation |
| snapshot_boundary | calendar_month_end when C is first-of-month; otherwise last_observed_date_partial_month | Explicit cutoff schedule inferred from observed dates | Even a calendar month-end cut does not establish complete capture |

All snapshots retain `synthetic=true` and `coverage_verified=false`. No extra final state, risk, contract or contact field is introduced. Signup-derived full-tenure flags remain opportunity flags, not verification.

## Calendar comparison eligibility

For a nominal N-day comparison require (1) some exported history before C, (2) signup age ≥ N days, and (3) `window_inside_export_span_Nd=true`. This conservative display mask avoids obvious pre-span or pre-signup comparisons. It does not verify entitlement or attendance capture. There is no minimum-event threshold selected for engagement. A represented member can have zero records in the current window; that is still only a zero export count. Calendar context after a contractual cancellation remains in the summaries and does not establish outreach eligibility.

## Derived analytical tables

| Export | Grain | Definitions and interpretation |
| --- | --- | --- |
| member_snapshots.csv | Member × exclusive cutoff | Existing 29 fields plus the six metadata fields above; unique composite key |
| snapshot_summary.csv | Cutoff | signed_up_roster = roster rows; members_with_exported_history = represented pre-C histories; no_exported_history = remainder. calendar_eligible_30d/60d/90d use the nominal masks above. median_visits_30d_calendar_eligible uses the 30-day mask; median_recency_days_represented uses represented histories. positive/zero/negative_30d_count_changes compare current30−previous30 in the 60-day mask; median_30d_count_change shares that denominator. eligible_60d_with_zero_previous30 counts zero baselines; coverage_verified_members is always zero. snapshot_boundary records the schedule type. |
| feature_diagnostics.csv | Feature at final cutoff | roster_rows and represented_members distinguish populations. non_null_roster / non_null_represented are usable counts; null_fraction_roster uses all final roster rows. distinct_values_represented, zero_fraction_of_nonnull_represented, minimum/p25/median/p75/maximum use only represented non-null values. Quantiles are descriptive, not thresholds. |
| window_sensitivity.csv | Final member with 90-day calendar eligibility | Existing metric/metadata columns for the identical comparison cohort. baseline_change_sign_agrees compares sign(current30−previous30) with sign(current30−preceding60/2), including zero as a distinct arithmetic sign. frequency_30d_minus_90d is the difference in nominal exported events/week. Neither column is an engagement state or validated classification. |
| same_volume_different_history.csv | Two illustrative members, if available | At final cutoff choose smallest positive shared visits_30d count with different deltas in 60-day eligible rows; select smallest and largest delta, with member ID as a deterministic tie-breaker. Descriptive example selection, not a representative sample. |

Plots: support by historical cutoff; member change heatmap with unavailable comparisons in gray; recency/volume and complete-week variability; identical-cohort window sensitivity; field support and distinct values. Source timezone remains unknown. Overlapping 30/90-day windows are dependent; member snapshots are repeated measures. No independent validation or significance test is implied.

## Acquisition readiness

`reports/longitudinal/readiness.json` records the actual unmet requirements: member-specific capture periods, timezone, effective access and operational calendar. [Observation coverage template](../handoff/observation_coverage_template.csv) is headers only, not fabricated completeness evidence. A row should describe one uninterrupted verified capture interval for one member and event stream, with evidence. Separate rows represent disjoint intervals; gaps remain unknown. Use explicit offset timestamps, retain the IANA source timezone, and document ingestion semantics. `capture_complete` requires affirmative provider/operator evidence, never inference from regular attendance. Entitlement and closures belong to separate effective-dated inputs.

Run `python scripts/analyze_longitudinal.py` after source acquisition and `python scripts/execute_notebooks.py --notebook 03b_longitudinal_eda.ipynb` to replay the new notebook. `python scripts/verify.py` checks both the original milestone and this extension. No source purchase, publication or unrelated dataset merge is required.
