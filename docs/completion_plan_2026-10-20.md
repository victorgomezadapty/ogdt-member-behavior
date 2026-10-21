# Authorized close — 20 October 2026

Work continues with the already inspected Berkeley source; no other source is added and no model is trained.
The real monthly source supports the 12 existing descriptive metrics. The regular set has
84,251 rows from 8,073 members; it shares 81,927 keys with Retention but differs in family exclusion
and prorated history. Populations and policies stay separate. Retrospective flags shape selection;
they are not features available in real time.

1. Build a standalone code notebook with no attached data and no dependency on the repository or Retention.
   Download from the primary source to temporary storage, check both hashes and show aggregates.
   Test a real private run on Kaggle and record the result and the actual environment.
2. Complete the six-document monthly handoff and pin its local revision. Admit into the core an optional adapter
   with its own population namespace, twelve metrics and independent checks of formulas, windows, nulls, cut-off
   and equivalence of every row of the reviewed export. Do not replace Retention's model.
3. Record the ADR, schema, capabilities, module registry and execution evidence together.

The primary page and README have not provided an explicit data redistribution license.
The package contains no ZIP, table or individual exports. The OGDT code license does not apply to those data.
The remote run is private; publishing a public version is a separate step. States, operational risk,
daily data and intervention effects stay out of scope without blocking this historical delivery.

**Update, 21 October 2026:** the public step was taken. The notebook is public on Kaggle (version 2, COMPLETE,
aggregate totals identical to the local run), the code is public on GitHub and an aggregate-only site is live.
No data, member IDs or member-level outputs were published.
