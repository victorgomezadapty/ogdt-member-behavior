"""Roadmap text for the deferred notebooks 04-06 (states, segmentation, behavioral risk).

These notebooks stay code-free on purpose: the available sources cannot validate states,
segments or risk. Each outline records the decision it would serve, the evidence it needs,
what today's monthly data can already show, and the gate before any implementation.
"""

COMMON_GATE = (
    "## Gate before any code\n\n"
    "1. Event-level check-ins with verified capture, time zone, closures, pauses and entitlement.\n"
    "2. A written operational decision that would change, reviewed with the people who make it.\n"
    "3. Thresholds calibrated on distributions and checked for stability over time, with an explicit "
    "'unknown' outcome when evidence is missing.\n"
    "4. Contractual outcomes kept in the Retention module; behavior features never borrow its labels.\n\n"
    "Neither the Berkeley monthly panel (counts per month, 1997–2001) nor the Mindweave synthetic sample "
    "meets gate 1. See `docs/behavioral_state_definition.md` and `handoff/module_spec.md`."
)

DEFERRED_NOTEBOOKS = [
    ("04_member_states.ipynb", "Member states", (
        "**Decision it would serve:** who needs onboarding support, routine service, a barrier review or a "
        "capture check, instead of one message for everyone.\n\n"
        "**Candidate states (hypotheses, not a taxonomy):** New, Highly engaged, Stable, Declining, "
        "Low engagement, Dormant, plus Unknown when capture is unverified.\n\n"
        "**What the monthly data already shows:** 30.4% of eligible regular months record no visit and "
        "16.1% of complete three-month windows have none (notebook 07, site). These describe volume; "
        "they do not assign anyone a state, because a monthly zero cannot separate absence from missing capture."
    )),
    ("05_segmentation.ipynb", "Segmentation", (
        "**Decision it would serve:** a different service, schedule or capacity choice per segment. "
        "A segmentation that changes no decision is not built.\n\n"
        "**Evidence it needs:** validated states first, then recency, frequency, trend and consistency with "
        "tenure and coverage, compared against what operations already does.\n\n"
        "**What the monthly data already shows:** month-to-month changes (39.8% fewer, 28.5% equal, 31.7% more "
        "visits) and population patterns by month of run. Clustering these monthly aggregates would produce "
        "groups without an operational meaning, so it is not attempted."
    )),
    ("06_behavioral_risk.ipynb", "Behavioral risk", (
        "**Decision it would serve:** when a person's attendance pattern justifies an optional, reviewed "
        "conversation about barriers.\n\n"
        "**Evidence it needs:** validated states, within-member baselines and independently adjudicated outcomes. "
        "Behavioral risk must never be presented as churn probability.\n\n"
        "**What exists today:** the separate Retention module holds a bounded historical target and benchmark on "
        "the same Berkeley population. This lab shares keys with it (81,927 rows matched) but imports none of its "
        "outcomes or scores, so attendance features cannot leak into a churn label."
    )),
]


def outline(title, body):
    """Markdown for one deferred notebook; the first cell must say 'deferred'."""
    return f"# {title} — deferred roadmap\n\n**Intentionally not implemented.** {body}\n\n{COMMON_GATE}"
