# Behavioral states — research proposal, not implemented

Update 19 October 2026: the active source is the real Berkeley monthly panel, assessed in `project_plan.md` and `data_readiness.md`. Monthly counts permit descriptive monthly trajectories only. No validated states are introduced; event-level recency/day/time definitions from the preserved synthetic sandbox cannot be transferred to monthly aggregates. Target/censoring remains separate in Retention. See `monthly_methodology.md`.

Milestone 1 provides observation and candidate metrics only. No rows receive final states; no thresholds, clusters or risk scores are generated. The public synthetic excerpt cannot verify absence of attendance.

| Candidate state | Evidence to explore later | Operational decision to validate |
| --- | --- | --- |
| New | Insufficient membership history for stable recency/frequency/trend | Support onboarding and first-visit access |
| Highly engaged | Sustained frequency, recent use and regularity against tenure-aware distributions | Support preferred scheduling/capacity |
| Stable | Attendance pattern remains within individual variability | Continue routine service; avoid unnecessary contact |
| Declining | Persistent within-member reduction beyond expected variation, with worsening gaps/consistency | Review barriers before considering optional support |
| Low engagement | Persistently low verified attendance opportunity-adjusted volume | Explore member goals and access constraints |
| Dormant | Verified absence over an individually/contextually justified interval | Confirm data capture and access status before action |

Labels are hypotheses, not a final taxonomy. A lower-volume member may be improving while a high-volume member is declining. A state should use recency, frequency, trend and consistency, with tenure, coverage and operational context. Low variability with zero events is not strong habit. Missing events or unknown capture should produce an unavailable/uncertain state, not Dormant.

Phase 2: acquire complete logs and timezone; account for closures, pauses, entitlement and planned attendance; examine distributions; calibrate candidate thresholds with operational review; assess sensitivity, temporal stability and minimum evidence; define state precedence and uncertainty explicitly. Later clustering must explain what decision differs by segment. Keep contract cancellation/renewal separate and link only via an independently specified Retention Module.
