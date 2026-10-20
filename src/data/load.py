from pathlib import Path
import hashlib
import json
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]


def load_tables(root=ROOT):
    raw = Path(root) / "data/raw"
    manifest = json.loads((raw / "manifest.json").read_text(encoding="utf-8"))
    for entry in manifest["files"]:
        if hashlib.sha256((raw / entry["local_path"]).read_bytes()).hexdigest() != entry["sha256"]:
            raise ValueError(f"Source checksum mismatch: {entry['local_path']}")
    tables = {name: pd.read_csv(raw / f"{name}.csv")
              for name in ("members", "checkins", "locations", "plans")}
    for table, columns in {"members": ["signup_date", "cancel_date"],
                           "checkins": ["checkin_datetime"]}.items():
        for col in columns:
            original = tables[table][col]
            parsed = pd.to_datetime(original, errors="coerce")
            if (original.notna() & parsed.isna()).any():
                raise ValueError(f"Invalid date in {table}.{col}")
            tables[table][col] = parsed
    return tables


def audit_tables(tables):
    m, c, l, p = (tables[k] for k in ("members", "checkins", "locations", "plans"))
    checks = {}
    for name, frame in tables.items():
        checks[f"{name}_missing_pk"] = int(frame.id.isna().sum())
        checks[f"{name}_duplicate_pk"] = int(frame.id.duplicated().sum())
        checks[f"{name}_nonpositive_pk"] = int((frame.id <= 0).sum())
    for name, col, parent in [("members", "plan_id", p), ("members", "location_id", l),
                               ("checkins", "member_id", m), ("checkins", "location_id", l)]:
        checks[f"{name}_{col}_missing_or_orphan"] = int((~tables[name][col].isin(parent.id)).sum())
    # Validated joins fail on ambiguous identifiers rather than multiplying events.
    j = c.merge(m[["id", "signup_date", "cancel_date", "location_id"]],
                left_on="member_id", right_on="id", suffixes=("", "_member"), validate="many_to_one")
    checks["duplicate_event_signature"] = int(c.duplicated(["member_id", "location_id", "checkin_datetime"]).sum())
    checks["duplicate_member_timestamp"] = int(c.duplicated(["member_id", "checkin_datetime"]).sum())
    checks["missing_checkin_timestamp"] = int(c.checkin_datetime.isna().sum())
    checks["missing_signup_date"] = int(m.signup_date.isna().sum())
    checks["missing_or_nonpositive_duration"] = int((c.duration_minutes.isna() | (c.duration_minutes <= 0)).sum())
    checks["missing_or_nonpositive_capacity"] = int((l.capacity.isna() | (l.capacity <= 0)).sum())
    checks["missing_or_negative_price"] = int((p.price.isna() | (p.price < 0)).sum())
    checks["invalid_plan_share"] = int((p.share.isna() | ~p.share.between(0, 1)).sum())
    checks["checkin_before_signup"] = int((j.checkin_datetime < j.signup_date).sum())
    checks["checkin_after_cancel_day"] = int((j.checkin_datetime.dt.normalize() > j.cancel_date).sum())
    checks["cancel_before_signup"] = int((m.cancel_date < m.signup_date).sum())
    checks["active_with_cancel_date"] = int((m.is_active & m.cancel_date.notna()).sum())
    checks["inactive_without_cancel_date"] = int((~m.is_active & m.cancel_date.isna()).sum())
    checks["cancel_reason_without_date"] = int((m.cancel_reason.notna() & m.cancel_date.isna()).sum())
    # Date-only cancellation cannot determine event ordering on the cancellation day.
    observations = {
        "checkins_on_cancel_day": int((j.checkin_datetime.dt.normalize() == j.cancel_date).sum()),
        "visits_away_from_home_branch": int((j.location_id != j.location_id_member).sum()),
        "multi_visit_member_days": int((c.groupby(["member_id", c.checkin_datetime.dt.normalize()]).size() > 1).sum()),
        "overlapping_sessions": 0,
        "observed_member_ids": sorted(c.member_id.unique().tolist()),
    }
    for _, visits in c.sort_values("checkin_datetime").groupby("member_id"):
        end = visits.checkin_datetime + pd.to_timedelta(visits.duration_minutes, unit="m")
        previous_max_end = end.cummax().shift(1)
        observations["overlapping_sessions"] += int((visits.checkin_datetime < previous_max_end).sum())
    return {"checks": checks, "observations": observations,
            "missing_values": {name: frame.isna().sum().to_dict() for name, frame in tables.items()},
            "all_hard_checks_pass": not any(checks.values())}
