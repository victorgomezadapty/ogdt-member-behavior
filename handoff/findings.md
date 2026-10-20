# Findings — Milestone 1

## Active real fitness research — 19 October 2026

Source suitability was reviewed before implementation. Berkeley provides real historical member/month attendance and contractual context for the same source population as Retention. The new regular-month policy selects 84,251 months from 8,073 members; it does not reproduce the published sample. The selected rows contain 397,354 recorded attendances, mean 4.72 per eligible month, median 3, with 30.4% recorded zeros. These are subset-specific, month-weighted descriptions, not current-gym estimates or state thresholds.

Adjacent eligible-month comparisons have 73,352 usable rows; complete three- and six-calendar-month windows have 64,347 and 43,690 respectively. Unknown or excluded months break runs instead of becoming zeros. Under the same source namespace and table hash, all 84,251 behavior keys match the original population used by Retention. The final 20 October inspection of its v0.5 canonical export matched 81,927 keys/current counts; our 2,324 extra rows are explained by its family-as-of exclusion. Its historical target now exists, but no outcomes or scores are imported here. Prior-month and three-month history availability also differ because it allows earlier prorated months; these metrics cannot replace its model inputs. The August 2000 club-1 overtime boundary shows why recorded positive attendance alone cannot establish eligibility.

Reusable lesson: validate domain, population linkage, grain and temporal availability before choosing features. Monthly data cannot support daily recency or time-of-day preference. Coverage endpoints and author flags govern retrospective selection, not predictive inputs. A shared dataset is necessary but insufficient for identical feature semantics: selection, window policy and timestamps must also be checked against the current export, not assumed from an earlier plan. [Full monthly report](../reports/berkeley/report.md); [definitions](../docs/monthly_methodology.md).

## Preserved synthetic findings

Synthetic public sample only. These are observations and reusable methodological lessons, not population estimates.

- 300 roster members, 2,000 visits, 32 members with exported visits; 268 have unknown attendance coverage.
- Cancel dates/reasons and is_active are public. 140 rows have cancellation dates. Contract fields must remain conceptually separate from attendance features.
- The selected cohort's median lifetime exported events is 55.0; median inter-event gap is 2.42 days. These values are not state thresholds.
- 48 session overlaps warrant investigation of event semantics; no rows were automatically dropped.
- Audit primary/foreign keys and sampling before modeling. A roster left join must distinguish no exported records from observed inactivity.
- Compare volume, recency, trend, consistency and tenure jointly; calendar boundaries, member entry and incomplete exposure change interpretation.
- Static plan/status values cannot be used as historical facts without effective dates. Source-clock timestamps need timezone metadata.
- Complete logs and operational context are prerequisites for actionable states. Synthetic seasonality or anomalies cannot establish real-gym causal effects.

All numerical results and figures: [Milestone 1 report](../reports/milestone_1.md). Definitions: [metric catalog](feature_catalog.csv). Phase 2 is proposed, not implemented.

## Observe extension — 18 October 2026

The unchanged synthetic source supports 24 retrospective event-time cutoffs and 4,197 member-snapshot rows. The extension advances descriptive longitudinal EDA while state calibration, segmentation and risk remain deferred. In the final matched 90-day calendar-opportunity cohort, 4 of 29 members have different arithmetic change signs when comparing against previous30 versus the preceding60 monthly-equivalent baseline. Definition sensitivity should be documented before state calibration; it is not disagreement against a validated engagement label.

Historical population support must be calculated before each cutoff rather than using later attendance to define earlier availability. Event-time correctness still cannot reconstruct historical ingestion or roster availability without a versioned acquisition ledger. Capture remains unverified for every row; calendar eligibility, same-volume examples and repeated measures do not remove selection, exposure or contractual-context limitations.

Reproducible outputs, sensitivity tables and five additional figures: [longitudinal report](../reports/longitudinal/report.md). Field definitions: [methodology](../docs/longitudinal_methodology.md). Required acquisition evidence: [readiness assessment](../reports/longitudinal/readiness.json).
