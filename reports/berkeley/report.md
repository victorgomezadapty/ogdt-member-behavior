# Real monthly behavior — Berkeley

**Gym Member Behavior & Engagement Intelligence · source review 19 October 2026; integration updated 20 October 2026**

Active research on monthly attendance with real historical gym data. The Mindweave synthetic sandbox stays separate. Suitability was reviewed before implementation: [plan](../../docs/project_plan.md), [data readiness](../../docs/data_readiness.md), [dictionary](../../docs/monthly_data_dictionary.md) and [definitions](../../docs/monthly_methodology.md).

## What the source can answer

We can describe monthly volume, change and consistency for the same population used by the Retention lab. The public table has no individual visits: it does not support days since the last visit, time of day, weekday, or exact 7/30/90-day windows. Provenance is the [author archive](https://eml.berkeley.edu/~sdellavi/data/gymdata.shtml); names and flags were checked against the Stata file, README and code in the ZIP. Months and metrics come from 1997–2001, not from a present-day gym.

## Population and selection before analysis

Source: **491,506 rows**, **10,241 IDs** and **21 variables**. The key `(id,time)` is unique. Main subset: **84,251 regular months from 8,073 members**, under policy `berkeley_regular_month_v1`. These counts do not reproduce the published 7,752-member sample or all of its exclusions.

| stage | rows | members |
| --- | --- | --- |
| All source calendar rows | 491506 | 10241 |
| Inside documented club span | 450051 | 10241 |
| Source review flags accepted | 372809 | 8606 |
| Regular contract months (1/2) | 84251 | 8073 |

The cascade applies filters in sequence; individual flags can overlap. It requires regular contracts 1/2, accepted flags and the documented period. Months without a contract, prorated, frozen, promotional, ambiguous or outside follow-up are excluded from the main analysis. The eligibility table keeps every original key and sets the analytical attendance of excluded months to null. **Excluded months are never imputed as zero.**

Club 11 has attendance in August 2000, but every row for that month has overtime=1 and is excluded. The main period therefore ends in July 2000 for that club and in February 2001 for the other two. Coverage is never decided from the mere presence of rows or positive counts.

After all filters are combined, eligible rows run from **1997-05-31** to **2001-01-31**. Published limits do not guarantee that every boundary month contributes eligible rows under this policy.

## Recorded attendance in eligible months

The selected months contain **397,354 recorded visits**: mean **4.72**, median **3.0**, and **30.4% of months with zero recorded**. The denominator is eligible member-months, not all members or all gym attendance. These zeros are kept; they are not Dormant or churn labels. The regular-month composition varies by club and month, and the chart does not validate seasonality or causal effects.

## Monthly trajectories and windows

There are **73,352 comparisons of adjacent eligible months**, **64,347 complete three-month windows** and **43,690 six-month windows**. Gaps and exclusions break every run; separated months are never compared as if they were consecutive.

Among valid comparisons: **23,259 positive differences**, **20,933 equal** and **29,160 negative**. These are arithmetic signs, not validated states. The percentage change is null when the previous month is zero. Run length is not called contract tenure, and distance to the last positive month is not turned into daily recency.

| metric | non_null_rows |
| --- | --- |
| recorded_attendance_month | 84251 |
| attendance_previous_month | 73352 |
| attendance_change_vs_previous_month | 73352 |
| attendance_pct_change_vs_previous_month | 52865 |
| attendance_sum_3_calendar_months | 64347 |
| attendance_mean_3_calendar_months | 64347 |
| attendance_std_3_calendar_months | 64347 |
| positive_attendance_months_3 | 64347 |
| attendance_sum_6_calendar_months | 43690 |
| attendance_mean_6_calendar_months | 43690 |
| consecutive_eligible_months | 84251 |
| months_since_recorded_positive_month | 77089 |

The six volume trajectories A–F keep nulls and breaks in excluded months; they are not segments or a probability sample. Monthly aggregation cannot reconstruct day or hour habits. A zero standard deviation across zero-attendance months does not demonstrate a stable habit either.

## Compatibility with Retention

The frozen ZIP is byte-identical to Retention's local source: `f2abbaa0312b697c56892621782073a8dd4b0fbf7cdbb8b9746a28c6398772f9`. Stata table: `e56ffe6177eb5e1508555d07a756a58f9e74d051eed12601ab5a34919949289c`. All **84,251 metric keys** match the shared original population using `(dataset_id, member_id, period_end)` with `dataset_id=berkeley_gym_aer_2006`.

The final check reflects the current state of Retention. Canonical export available: **True**. Canonical rows matched: **81,927**; rows only in Member Behavior: **2,324**. When the export exists, current counts and month boundaries are checked for equality. Population differences are explained by family observed to date, which Retention excludes; our windows are also stricter and do not include its earlier prorated months. Feature names and transformations are not interchangeable for its model.

Retention already has its own target **berkeley_clear_transition_v1** and a historical benchmark in its module, according to the inspected contract. **No outcomes or scores are imported here**, that model is not retrained and no operational use is promoted. If the export is unavailable, verification is limited to source and original keys, as the JSON records. [Updated compatibility evidence](integration_readiness.json).

Berkeley members are never linked with Mindweave or Lisbon. The verification code rejects different namespaces or hashes even when IDs look alike. No Retention file was changed. [Integration evidence](integration_readiness.json).

## Limits and next step

The design describes regular months of a historical sample; it does not fully reproduce the paper's filters or validate behavior in present-day gyms. Flags and follow-up ends shape a retrospective selection. They are not predictors, and the archive has no ingestion clock. For research, the aggregate is assumed to be available at month close; this is not demonstrated for production.

Retention's own target is restricted to recorded discontinuity between clear states and keeps other outcomes unknown; it is not permanent churn or present-day gym scoring. Code 7 is not turned into churn here. No model was trained in this lab, and no engagement states, clusters or risk were assigned. Redistribution terms must be resolved before original rows or identifiable derivatives are published. Person-level files stay local and are ignored by Git.

The next viable step is to review core admission and the selection/history policy across consumers, keeping behavior features and future outcomes separate. Retention's existing benchmark keeps its own limits and target definition. This feature comparison does not demonstrate intervention effects or validate engagement states. No daily detail needs to be invented, and no clustering is needed to complete this descriptive phase.

## Reproduce

`python scripts/acquire_berkeley.py --download` (or `--source ../ogdt-retention/data/raw/berkeley/data.zip`), then `python scripts/analyze_berkeley.py`, `python scripts/execute_notebooks.py --notebook 07_berkeley_monthly_eda.ipynb` and `python scripts/verify_berkeley.py`. See the [monthly contract](../../handoff/monthly_data_contract.yaml) and [catalog](../../handoff/monthly_feature_catalog.csv). Source review and processing do not alter the target or the Retention lab.

## Figures

### Calendar rows are filtered before describing attendance

![Calendar rows are filtered before describing attendance](figures/01_selection_audit.png)

### Monthly support and recorded attendance by source club

![Monthly support and recorded attendance by source club](figures/02_monthly_patterns.png)

### Monthly volume and member-level means use different weights

![Monthly volume and member-level means use different weights](figures/03_attendance_distributions.png)

### Within-member changes require adjacent eligible months

![Within-member changes require adjacent eligible months](figures/04_changes_and_support.png)

### Six volume-rank examples preserve unavailable-month gaps

*Kept local only.* This figure shows six individual members' monthly series. Redistribution rights for the source are not established, so it is excluded from Git and every public output.

