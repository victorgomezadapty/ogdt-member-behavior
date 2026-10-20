"""Pinned real-fitness monthly source. Never interpret calendar padding as capture."""
from pathlib import Path
from datetime import datetime, timedelta
import hashlib
import io
import zipfile
import numpy as np
import pandas as pd

DATASET_ID = "berkeley_gym_aer_2006"
ARCHIVE_SHA256 = "f2abbaa0312b697c56892621782073a8dd4b0fbf7cdbb8b9746a28c6398772f9"
TABLE_SHA256 = "e56ffe6177eb5e1508555d07a756a58f9e74d051eed12601ab5a34919949289c"
POLICY_ID = "berkeley_regular_month_v1"
KEY = ["dataset_id", "member_id", "period_end"]
PAPER_START = pd.Timestamp("1997-04-01")
PAPER_LAST_MONTH = {11: pd.Timestamp("2000-07-01"), 13: pd.Timestamp("2001-02-01"), 16: pd.Timestamp("2001-02-01")}
SOURCE_COLUMNS = {"id", "time", "attend", "contract", "imprice", "trprice", "code", "init", "problem", "club", "birthday", "female", "age", "month", "begatt", "endatt", "endcont", "endcontp", "overtime", "dlocker", "duplicate"}


def matlab_dates(values):
    numeric = pd.to_numeric(values, errors="raise")
    if numeric.isna().any() or not np.isfinite(numeric).all() or (numeric != np.floor(numeric)).any():
        raise ValueError("Expected finite integral MATLAB daily dates")
    mapping = {v: pd.Timestamp(datetime.fromordinal(int(v))-timedelta(days=366)) for v in numeric.unique()}
    return numeric.map(mapping)


def validate_source(frame):
    required = ["id", "time", "attend", "contract", "club", "duplicate", "problem", "overtime", "begatt", "endatt"]
    if not set(required).issubset(frame) or frame[required].isna().any().any():
        raise ValueError("Missing source fields or required values")
    if frame.duplicated(["id", "time"]).any():
        raise ValueError("Source member/month keys must be unique")
    for col in ["id", "attend", "contract", "club", "duplicate", "problem", "overtime"]:
        v = frame[col]
        if not np.isfinite(v).all() or (v != np.floor(v)).any() or (v < 0).any():
            raise ValueError(f"Invalid nonnegative integral field: {col}")
    if (frame.id <= 0).any() or not frame.club.isin(PAPER_LAST_MONTH).all():
        raise ValueError("Unknown member/club identity")
    if not frame.duplicate.isin([0, 1]).all() or not frame.overtime.isin([0, 1]).all():
        raise ValueError("Unknown source binary flag")
    if not frame.contract.isin([0, 1, 2, 7, 11, 14, 15, 19, 20, 21, 24, 25, 27, 70, 77, 111]).all():
        raise ValueError("Review undocumented source contract code before use")
    dates = matlab_dates(frame.time)
    if not dates.dt.day.eq(1).all():
        raise ValueError("Expected source calendar months, not visit timestamps")
    return dates


def load_berkeley(path):
    content = Path(path).read_bytes()
    if hashlib.sha256(content).hexdigest() != ARCHIVE_SHA256:
        raise ValueError("Source archive hash changed; reassess before processing")
    with zipfile.ZipFile(io.BytesIO(content)) as archive:
        table = archive.read("GymAERSourceData.dta")
        if hashlib.sha256(table).hexdigest() != TABLE_SHA256:
            raise ValueError("Source table hash mismatch")
        with pd.read_stata(io.BytesIO(table), iterator=True, convert_categoricals=False) as reader:
            labels = reader.variable_labels()
            frame = reader.read()
    if set(frame) != SOURCE_COLUMNS:
        raise ValueError("Unexpected source schema")
    validate_source(frame)
    return frame, labels


def monthly_observations(source):
    month = validate_source(source)
    first = matlab_dates(source.begatt)
    last = matlab_dates(source.endatt)
    in_span = month.ge(first) & month.le(last) & month.ge(PAPER_START) & month.le(source.club.map(PAPER_LAST_MONTH))
    review_ok = source.duplicate.eq(0) & source.problem.eq(0) & source.overtime.eq(0)
    regular = source.contract.isin([1, 2])
    eligible = in_span & review_ok & regular
    out = pd.DataFrame({"dataset_id": DATASET_ID,
                        "member_id": source.id.astype("int64").astype(str),
                        "period_end": month.dt.to_period("M").dt.to_timestamp("M"),
                        "club_id": source.club.astype("int64"),
                        "source_contract_code": source.contract.astype("int64"),
                        "excluded_outside_documented_span": ~in_span,
                        "excluded_author_duplicate": source.duplicate.ne(0),
                        "excluded_author_problem": source.problem.ne(0),
                        "excluded_overtime": source.overtime.ne(0),
                        "excluded_nonregular_contract": ~regular,
                        "attendance_eligible": eligible,
                        "recorded_attendance_month": source.attend.where(eligible).astype(float)})
    out["eligibility_status"] = np.where(eligible, "regular_month_in_documented_span", "excluded_see_reason_flags")
    # Reason flags are audit metadata, never behavioral predictors or churn labels.
    return out.sort_values(["member_id", "period_end"], key=lambda s: s.astype(int) if s.name == "member_id" else s).reset_index(drop=True)


def assert_same_population(left, right, left_table_sha256, right_table_sha256):
    """Reject ID-only joins and mismatched populations, even if values coincide."""
    for frame in [left, right]:
        if not set(KEY).issubset(frame) or frame[KEY].isna().any().any() or frame.duplicated(KEY).any():
            raise ValueError("Unique complete namespaced member/month keys are required")
        if not frame.dataset_id.eq(DATASET_ID).all():
            raise ValueError("Unrelated dataset/population: member join prohibited")
    if left_table_sha256 != TABLE_SHA256 or right_table_sha256 != TABLE_SHA256:
        raise ValueError("Source table identity must match the inspected Berkeley table")
    # Matching source identity permits different eligibility subsets. Join only on KEY.
    return left[KEY].merge(right[KEY], on=KEY, how="inner", validate="one_to_one")
