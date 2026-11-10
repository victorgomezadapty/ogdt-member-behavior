# Methodology

## Lisbon: Sport Services Dataset (CC BY 4.0)

- Unit: one user (membership) of one sports facility; 14,942 users who enrolled between 2 June 2014 and 21 October 2019.
- Length: `EnrollmentFinish - EnrollmentStart`, in days divided by 30.4375.
- Event: `Dropout = 1` (11,968 users, 80.1%). The 2,974 users with `Dropout = 0` are censored at `EnrollmentFinish`, which is 31 October 2019 for all of them.
- Survival: Kaplan-Meier product-limit estimator, Greenwood variance, log-log 95% interval. Implemented in `src/analysis.py` and tested against a hand-worked example.
- Groups: average weekly visits (`AverageFrequency`: under 0.5, 0.5 to 1, 1 to 2, 2 or more), renewals (`NumberOfRenewals`: 0, 1, 2, 3 or more), classes (`AttendedClasses` above 0).
- Recency: `DaysWithoutFrequency`, the days between the last recorded visit and the end of the membership record.
- Every grouping variable is measured over or at the end of the membership. The results describe how memberships unfolded; they are not baseline predictors. Renewals are mechanically tied to length.

## Carrera et al. replication data (CC0 1.0)

- Unit: one participant; 1,292 existing members of a US gym who joined a 4-week incentive study.
- Weekly visits `previsits1` (1 week before the study) to `previsits8` (8 weeks before) come before any intervention.
- Week-to-week: the 7 adjacent pairs per person (9,044 pairs). Pearson r of counts; share with a visit next week given a visit, or none, this week.
- Month-to-month: visits in weeks 5 to 8 vs weeks 1 to 4 (`past4`). Pearson r, and AUC (ties counted as 0.5) for ranking who records any visit in weeks 1 to 4.
- Control group only (427 people, no incentive): `past4` vs `visits` (4 study weeks) and vs `visits_next4weeks`.
- Intervals: 1,000 bootstrap resamples of people, stratified by control vs incentive arm, percentile 95%, seed 20261110.

## Dropped

The earlier monthly contract-state and month-to-month transition analysis was removed. It relied on an archive without an open licence, and no openly licensed dataset records gym contracts month by month. The earlier synthetic sandbox was also removed.

## Consistency with the Retention lab

Both labs read the same Lisbon file (SHA-256 `775f226bef749497017579a9088e5f83249d8f1916c27d8d89acc189bccaa04d`) and report the same totals: 14,942 users, 11,968 dropouts, 80.1%. `src/analysis.py` asserts these totals on every run.
