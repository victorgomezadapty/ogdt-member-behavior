# Source suitability and decision — 19 October 2026

This assessment precedes the implementation of the monthly adapter. It is based on primary documentation and on inspecting the actual local file, not on a dataset's commercial name.

**Final update, 20 October:** the initial state is kept below as assessment history. Retention v0.5 now has its own monthly target and historical benchmark; its real export of 81,927 monthly features was compared with Member Behavior. Every key matches, and the 2,324 additional rows in our subset are explained by family observed up to t. Current counts and time boundaries agree. Historical windows follow different policies, so the features are not direct substitutes for Retention's model inputs. No outcomes or scores were loaded. Exact evidence and the export and contract hashes are in [integration](../reports/berkeley/integration_readiness.json).

Retention's current report declares primary equivalence of the Lisbon CSV and an adjudicated target; mentions of those open items in the initial assessment no longer describe its current state. This lab keeps Lisbon out of its pipeline and does not claim an independent primary verification of that file.

| Criterion | Berkeley | Mindweave | Lisbon |
| --- | --- | --- | --- |
| Domain and origin | Real gyms; author's public replication source | Simulated gym chain; public synthetic sample | Real sports facility per primary record; local CSV in Retention obtained from a mirror |
| Unit | Person-month; 21 columns | Member, synthetic check-in, plan, branch | Aggregated person; no free monthly panel |
| Identity and linkage | Unique `(id,time)`; same source and hash as Retention | IDs from another population, no link with Berkeley | Another population; joining people with the other sources is forbidden |
| Behavior | `attend`, monthly count | Clocked events, incomplete capture | Usage and end-of-relationship aggregates; snapshots must not be reconstructed |
| Time and coverage | Raw calendar 1997-01 to 2001-03; limits and overtime per club | Dates 2023–2024; only 32 members with visits | The acquired CSV includes dates and end-of-relationship summaries; semantic inspection belongs to Retention |
| Contractual outcomes | Detailed `contract`; target and censoring pending | Synthetic cancel_date/is_active | The source's own dropout, not automatically equivalent |
| Scope accepted here | Descriptive research on monthly attendance in regular contracts; shared interface | Preserved sandbox, not real evidence | Outside the new pipeline; later independent comparison |

## Verified directly

- ZIP and Stata hashes match the source audited in Retention. Similar-looking IDs from different populations are never reused.
- 491,506 rows, 10,241 IDs, 51 calendar months, unique keys and no gaps in the raw grid per ID. The grid includes months without a contract; it does not demonstrate continuous follow-up.
- `attend` is a non-negative integer (0–42). Flags and follow-up limits exist; missing demographics are not imputed because they are not used.
- `duplicate` marks 1,234 rows even though `(id,time)` is unique: it flags an author-identified person-record problem, not an ordinary duplicate key.
- 16,532 rows have `overtime=1` and 76,909 have `problem != 0`. They are audited and excluded from the main subset.
- Club 11 has 5,181 recorded visits in August 2000, a month marked overtime for all 4,468 of its rows. It is excluded rather than presented as regular capture.
- Main months before computing metrics: 84,251 regular rows from 8,073 members, after explicit filters. This count does not reproduce the paper's sample.

## Assumptions and open items

- Availability at month close is assumed in order to study retrospective features; the file keeps no ingestion or historical revisions. This is not a production point-in-time evaluation.
- Regular months are selected conservatively, not as proof of perfect follow-up. The paper discusses possible recording errors; an eligible zero is a recorded monthly zero, not proven absolute absence.
- The paper's complete exclusions, contracts, proration and spells are still not reproduced. Do not call this the 7,752-person sample or assign a join date from the left edge.
- Contract end, voluntary exit, freezing and non-payment need definition and censoring in Retention. No labels are assigned and its end-of-follow-up variables are never mixed with behavior predictors.
- Redistribution terms for the Berkeley archive are unresolved. This is local research work; raw data and person-level derivatives stay out of Git and out of any publication.
- Equivalence of the Lisbon CSV with the primary source bytes is pending; Retention's manifest records an attributed mirror. This continuation does not process or modify those files.

## Decision

**Suitable for monthly behavior EDA, with audited selection and coverage. Not yet suitable for validated states, churn prediction or operational intervention.** Adopting Berkeley as Member Behavior's active research shares a real identity with Retention; Mindweave is kept as software and methodology evidence that is exclusively synthetic.

References: [Berkeley](https://eml.berkeley.edu/~sdellavi/data/gymdata.shtml), [paper and data appendix](https://eml.berkeley.edu/~sdellavi/wp/gymemp06-03-19.pdf), and the README and original code inside the ZIP. Retention's assessment was consulted in `../ogdt-retention/docs/project_plan.md` and `../ogdt-retention/docs/data_readiness.md`; both are left untouched.
