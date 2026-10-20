# Methodology — Observe Member Behavior

## Scope and provenance

Descriptive observation only, synthetic public sample. Download all substantive CSV tables and the source card from a fixed Hugging Face revision. Record SHA-256, source URL, retrieval time and file sizes; verify hashes on each analysis. No ML, state labels, risk scores or cross-dataset merging.

## Auditing before interpretation

Inspect all schema fields, parsed types, distinct counts, date bounds and null counts; identify primary/foreign keys; audit duplicate IDs/signatures, orphan references, missing dates, numeric validity, cancellation/signup chronology and contract-status consistency. Count same-day repeats and overlapping durations as review flags. Preserve raw events; no cleaning is silently inferred from counts. Join with cardinality validation. Audit results are machine readable; actual schema determines availability.

## Observation populations

Roster: 300 exported member snapshots. Attendance cohort: 32 members with at least one exported check-in. The latter is selected using the full export and is suitable only for descriptive summaries, not unbiased prospective cohort analysis. The other 268 receive unknown/null attendance metrics; no final state is assigned. All rows have unverified event capture.

For week/month panels, enumerate calendar periods after signup, limited to the first/last observed event dates. Record calendar opportunity days and flag partial periods. Zero export periods are shown, including post-contract-event time, to make truncation/context visible. They are not membership exposure or evidence of dormant states. Member trajectories use monthly counts; six illustrative members are selected at evenly spaced total-volume ranks, not selected for a desired narrative.

## Temporal rules

Source timestamps remain timezone-naive. The reference feature cutoff is the midnight following the final recorded date: `2024-12-29 00:00`, exclusive. Trailing windows are `[cutoff − N days, cutoff)`; events on/after cutoff are excluded. Last-visit recency is calendar days between the cutoff date and the last exported visit date. Report that the final calendar day may be incomplete.

Rates use fixed full-tenure 30/90-day windows and report exported events per nominal week. Insufficient tenure yields null rates/trends. Coverage is still unverified, so eligible tenure does not establish eligible attendance exposure. Compare current 30 days with prior 30 days or the preceding 60 days' 30-day equivalent; the latter avoids including the current window in its own baseline. A zero prior denominator yields null percent change, not infinity or an assigned state.

Consistency uses eight complete Monday–Sunday weeks preceding the cutoff's current partial week. Count weeks with an exported event and population standard deviation of eight weekly event counts. Less than full signup opportunity for those weeks yields null consistency. This is not habit strength. Preferences and branch diversity use the last 90 days; ties are explicitly listed and visit support is retained.

## Distributions and seasonality

Use raw event counts, represented-member support, medians/IQRs, daily timeline, calendar panels, tenure event bins, clock-hour counts, source-plan/home-branch context and individual trajectories. Day-of-week totals are also divided by calendar-day occurrences; this corrects day-count imbalance only. Monthly export density uses selected members' calendar days, not entitlement or verified capture. Tenure bins are descriptive, not calibrated states; counts are not directly comparable across unequal bin lengths or follow-up. Show month-of-year by year and signup counts separately. No inferential seasonality or anomaly claim is made.

## Reusability and later work

Every output feature has a definition, business meaning, window, requirements and limitations in the handoff catalog. Contact fields and contract outcomes are excluded from feature construction. Tests cover cutoff leakage, window edges, unknown versus zero, insufficient tenure, zero baselines and cancellation independence. Offline verification checks sources, joins, output counts, catalog agreement, notebooks and artifacts. Phase 2 must establish verified exposure before calibrating states or exploring decision-relevant segmentation.
