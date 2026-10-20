# Data dictionary

Synthetic public sample; generated from all four downloaded tables. Counts reflect the pinned revision. See `data/raw/manifest.json` for source hashes.

## members (300 rows)

| Field | Parsed type | Nulls | Distinct non-null | Observed range / examples | Meaning / caveat |
| --- | --- | --- | --- | --- | --- |
| id | int64 | 0 | 300 | 1 → 300 | Member identifier; candidate primary key. |
| first_name | str | 0 | 15 | [contact field omitted] | Synthetic given name; excluded from analytics. |
| last_name | str | 0 | 15 | [contact field omitted] | Synthetic family name; excluded from analytics. |
| email | str | 0 | 300 | [contact field omitted] | Synthetic contact address; unnecessary for behavior metrics. |
| phone | str | 0 | 300 | [contact field omitted] | Synthetic phone; unnecessary for behavior metrics. |
| signup_date | datetime64[us] | 0 | 223 | 2023-01-01 00:00:00 → 2024-12-21 00:00:00 | Date-only signup; proxy membership start, not first visit. |
| plan_id | int64 | 0 | 5 | 1 → 5 | Current/static plan reference; no plan history. |
| location_id | int64 | 0 | 3 | 1 → 3 | Home branch reference; may differ from visit branch. |
| is_active | bool | 0 | 2 | True, False | Undated contract status snapshot; not attendance engagement. |
| cancel_date | datetime64[us] | 160 | 125 | 2023-02-01 00:00:00 → 2024-12-28 00:00:00 | Nullable date-only contractual cancellation field. |
| cancel_reason | str | 160 | 8 | Health issues, Dissatisfied with facilities, Not using enough, Financial reasons, Found another gym | Nullable synthetic cancellation reason; no outcome modeling here. |

## checkins (2,000 rows)

| Field | Parsed type | Nulls | Distinct non-null | Observed range / examples | Meaning / caveat |
| --- | --- | --- | --- | --- | --- |
| id | int64 | 0 | 2000 | 1 → 2000 | Visit identifier; candidate primary key. |
| member_id | int64 | 0 | 32 | 1 → 32 | Member reference. |
| location_id | int64 | 0 | 3 | 1 → 3 | Visited branch reference. |
| checkin_datetime | datetime64[us] | 0 | 1997 | 2023-01-12 18:26:00 → 2024-12-28 09:33:00 | Naive timestamp; source timezone and acquisition completeness unknown. |
| duration_minutes | int64 | 0 | 108 | 15 → 151 | Reported session duration in minutes; not measured exercise quality. |

## locations (3 rows)

| Field | Parsed type | Nulls | Distinct non-null | Observed range / examples | Meaning / caveat |
| --- | --- | --- | --- | --- | --- |
| id | int64 | 0 | 3 | 1 → 3 | Branch identifier; primary key. |
| name | str | 0 | 3 | IronFit Downtown, IronFit Eastside, IronFit Pearl District | Synthetic branch label. |
| capacity | int64 | 0 | 3 | 100 → 150 | Reported capacity; unit/occupancy interpretation undocumented. |
| has_pool | bool | 0 | 2 | True, False | Boolean pool availability. |

## plans (5 rows)

| Field | Parsed type | Nulls | Distinct non-null | Observed range / examples | Meaning / caveat |
| --- | --- | --- | --- | --- | --- |
| id | int64 | 0 | 5 | 1 → 5 | Plan identifier; primary key. |
| name | str | 0 | 5 | Basic Monthly, Premium Monthly, Basic Annual, Premium Annual, Student | Plan label; includes annual, monthly, student. |
| price | float64 | 0 | 5 | 19.99 → 499.99 | Price; currency and billing semantics not fully documented. |
| share | float64 | 0 | 5 | 0.08 → 0.35 | Reported plan-share parameter; not measured member proportion. |

Missing cancellation fields coincide with the 160 active-status rows in this revision. This is structural missingness; it does not establish future retention. Dates carry no timezone; cancellation dates lack within-day ordering. Plan shares sum to 1.00.
