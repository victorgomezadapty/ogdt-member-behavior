# Reproducible results of the monthly handoff

Raw source: 491,506 rows, 10,241 IDs, 21 columns, January 1997–March 2001, with calendar padding.
Own selection: 84,251 regular rows, 8,073 members, May 1997–January 2001; it does not reproduce the paper's 7,752.
397,354 recorded visits, mean 4.7163 per eligible month, median 3; 30.3735% of eligible months record zero.
Adjacent comparisons: 73,352; complete three-month windows: 64,347; six-month windows: 43,690.
These counts describe the cohort, with no inference interval or causal effect.

All 81,927 Retention v0.5 keys match in source and current count; the 2,324 extra rows here
correspond to its exclusion of families observed up to t. Its history allows some earlier prorated
months (11/21), while only 1/2 are used here. Do not substitute these metrics in its model.
No outcomes, scores or models were imported, and no other model was fitted.

Reproduction: `python scripts/verify_berkeley.py`; `python scripts/build_kaggle.py` creates the portable notebook.
The real Kaggle run finished COMPLETE and reproduced these figures, first privately and then as public version 2.
Environment and evidence: [kaggle_validation.json](../reports/berkeley/kaggle_validation.json). The local report
includes five audit figures; the published [full results](../reports/berkeley/report.md) show the four aggregate ones.

Temporal tests cover gaps, incomplete windows, zeros, unknown recency, invariance to the future,
overtime boundaries and rejection of incompatible keys. Artificial fixtures validate software;
the Berkeley results are real historical evidence, not current operational validation.
