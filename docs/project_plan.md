# Current plan — monthly behavior with a real fitness source

Decision recorded on **19 October 2026**, before the monthly adapter was built. The workspace memory, the Retention plan and assessment, primary documentation and the original archive were reviewed. The lab keeps its question: understand attendance trajectories without equating behavior, engagement and contractual exit.

## Closing update — 20 October 2026

Retention moved forward during execution. Its v0.5 contract and its `berkeley_clear_transition_v1` definition now adjudicate a bounded historical target; it has its own benchmark and a canonical export. Those documents were re-read and the actual export was compared: **81,927 shared keys**, equal current counts and equivalent month boundaries. **2,324 additional Member Behavior rows** are explained by Retention's exclusion of families observed up to t. Its windows also admit earlier prorated months (11/21), while this lab requires regular months (1/2). These features do not automatically replace those in its model. Outcomes and scores stay separate and Retention is not modified. See `reports/berkeley/integration_readiness.json`.

References to a pending target or acquisition in the sections below record the initial assessment of 19 October; this update takes precedence for the current state. Retention also reports that the primary equivalence of the Lisbon CSV is verified; Member Behavior neither processes that file nor re-validates the equivalence. Operational use, real ingestion, ambiguous states and generalization to present-day gyms remain unvalidated.

## Assessment during planning

**Berkeley, Paying Not to Go to the Gym**, comes from real gyms. `GymAERSourceData.dta` inside the author ZIP was inspected: 491,506 rows, 10,241 identifiers, 21 columns and a unique `(id,time)` key. The public file is member-month; `time` marks the start of the month as a MATLAB date and `attend` is the monthly count. Its raw calendar covers January 1997–March 2001 and includes months outside follow-up and without a contract. Having a row is not the same as having attendance exposure. The paper and the author's code complement the file's labels.

**Mindweave** remains useful to test software with synthetic events. Its 2,000 check-ins cover only 32 of 300 members; that sample does not validate real behavior and must not be expanded to look like fitness evidence. Its notebooks, metrics and reports are kept as methodological reference, separate from Berkeley.

**Lisbon** is a different population. Its primary documentation describes real data from a sports facility. Retention already holds a CSV acquired from a mirror with recorded provenance; byte-for-byte equivalence with the primary file is not confirmed. Its aggregated end-of-relationship fields cannot build a historical monthly sequence. This milestone does not process it or join it with Berkeley.

## Scope the data supports

1. Freeze the ZIP already acquired by Retention locally, check hashes and keep original names and labels. Do not modify Retention or publish the original data.
2. Audit months, flags, codes and boundaries per club. Separate calendar-row coverage from contractual eligibility.
3. Build a descriptive monthly adapter keyed by `(dataset_id, member_id, period_end)` with calendar-month window metrics. Do not turn them into daily visits or exact 30/90-day windows.
4. Use an explicit subset of regular months as the main analysis: `contract in {1,2}`, `duplicate=0`, `problem=0`, `overtime=0`, and dates inside the attendance limits and the period published for each club. Excluded months stay audited; their analytical attendance is unknown or not applicable, never an imputed zero.
5. Compare adjacent months and compute three- and six-month windows only when every consecutive month has eligible attendance. Never bridge gaps or frozen, prorated or out-of-capture months. Keep the zeros that are actually recorded in eligible months.
6. Describe distributions, the time path and individual variation with explicit denominators. Deliver a monthly dictionary, report, notebook and integration contract.

## Boundaries and verified decisions

Club 11 has rows for August 2000 with positive attendance but `overtime=1`; they are excluded. The published period ends in July 2000 for that club and in February 2001 for clubs 13 and 16. These limits are combined with source metadata; `time <= endatt` alone is not enough.

The 491,506 rows contain 374,853 contract codes equal to 0. They are not 374,853 cases of disengagement. Code 7 mixes freezing and cancellation within the month; 70 identifies non-payment in the documentation; neither becomes a churn target in this lab. The main selection deliberately excludes those months.

The published 7,752-member sample is not reproduced: the complete spell, family and promotion exclusions are missing. The subset is labelled **regular contract months of the raw source**, with its own figures and limits. Tenure is not reconstructed from the first visible month as if it were the real join date.

## Linkage and timing

The inspected ZIP has SHA-256 `f2abbaa0312b697c56892621782073a8dd4b0fbf7cdbb8b9746a28c6398772f9`, matching Retention's source; its table has SHA-256 `e56ffe6177eb5e1508555d07a756a58f9e74d051eed12601ab5a34919949289c`. The keys are `dataset_id=berkeley_gym_aer_2006`, `member_id=str(int(id))` and `period_end` as the last calendar day. This is verified population and source compatibility, not permission to use labels that are not yet adjudicated.

Month-close metrics use only the current and past months. Availability at that close is a research assumption; there is no ingestion clock. Extract end dates, flags and retrospective corrections shape selection and audit, but are not predictors. The contractual target and follow-up stay in Retention, still pending adjudication at the time of this plan. No models are trained and no final states are assigned in this continuation.

## Open items and acceptance criteria

Verify key preservation, nulls across gaps, windows without future information and exact compatibility with the shared archive; keep executable evidence. Document redistribution permissions before publishing original rows or identifiable derivatives. Do not extrapolate this historical study to present-day gyms, Optimo or intervention decisions. States, segments and risk require a later phase with explicit semantics, objective and validation.

Primary sources: [author data page](https://eml.berkeley.edu/~sdellavi/data/gymdata.shtml), [paper](https://eml.berkeley.edu/~sdellavi/wp/gymemp06-03-19.pdf), and the README and `DataGymAERMar06.do` inside the inspected archive. [Lisbon: primary record](https://data.mendeley.com/datasets/yprk4jdgnv/1). Further provenance and decisions are in `docs/data_readiness.md`.
