# Admitted definitions · monthly Member Behavior

Contract: [monthly_data_contract.yaml](monthly_data_contract.yaml).
Full catalog: [monthly_feature_catalog.csv](monthly_feature_catalog.csv).
Real Berkeley source, selection `berkeley_regular_month_v1`; grain member × calendar month.
These monthly documents form the active six-part handoff. Files without the monthly
prefix keep the synthetic sandbox and do not replace this contract.

Let x(t) be the recorded count in an eligible month. Only eligible rows are published. A missing
or excluded month breaks the run. Windows include month t; every input must be observed in
consecutive months. The available close is 00:00 on the day after the month ends, a research proxy
without a verified ingestion clock. Flags and boundaries are used retrospectively for selection,
not as features. Daily attendance is not reconstructed.

| Metric | Formula / unit | Null when |
| --- | --- | --- |
| recorded_attendance_month | x(t), recorded visits | Never null in an eligible row; zero is valid |
| attendance_previous_month | x(t-1), visits | Previous month ineligible or missing |
| attendance_change_vs_previous_month | x(t)-x(t-1), difference in visits | Comparison not available |
| attendance_pct_change_vs_previous_month | x(t)/x(t-1)-1, fraction | Previous month missing or zero |
| attendance_sum_3_calendar_months | Σ x from t-2 to t, visits | Fewer than 3 complete consecutive months |
| attendance_mean_3_calendar_months | Sum above / 3, visits per month | Same support |
| attendance_std_3_calendar_months | √(Σ(x-mean)²/3), ddof=0 | Same support |
| positive_attendance_months_3 | Σ 1[x>0] over 3 months, months from 0 to 3 | Same support |
| attendance_sum_6_calendar_months | Σ x from t-5 to t, visits | Fewer than 6 complete consecutive months |
| attendance_mean_6_calendar_months | Sum above / 6, visits per month | Same support |
| consecutive_eligible_months | Length of the observed run up to t, months | Always ≥1; not contract tenure |
| months_since_recorded_positive_month | Calendar distance to the last x>0 in the run, months | No known positive month in the run |

Report means pool member-month rows with a non-null metric. The denominator is that number of
rows, with repeated people; it is not all original members or a sample weighted equally per
member. Support and the number unavailable are reported for every metric. Zero variability can
come from repeated zeros. Run length and recency are monthly support and proxy, not a validated habit.

Admitted use: describe volume, changes and historical support. It does not enable states, probabilities,
outreach, daily visits or causality. [Detailed methodology](../docs/monthly_methodology.md).
