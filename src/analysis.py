"""Member behavior analysis on two open sources. Same code runs in the notebook.

Lisboa (CC BY 4.0): one row per user of a sports facility, 2014-06 to 2019-10.
  Membership length = EnrollmentFinish - EnrollmentStart; event = Dropout; users without
  a dropout are censored at the extraction date (2019-10-31). Frequency, renewals,
  classes and days without a visit are measured over or at the end of the membership,
  so they describe how memberships ended; they are not baseline predictors.
Carrera et al. (CC0): 1,292 gym members, weekly visits for the 8 weeks before a study,
  4-week totals before, during and after it. Persistence uses only pre-study weeks,
  plus the control group (no incentive) for the study and follow-up periods.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

SEED = 20261110
N_BOOT = 1000
DAYS_PER_MONTH = 30.4375
FREQ_BANDS = [(0, 0.5, "<0.5"), (0.5, 1.0, "0.5-1"), (1.0, 2.0, "1-2"), (2.0, np.inf, "2+")]
RECENCY_BANDS = [(0, 7, "0-7"), (8, 30, "8-30"), (31, 60, "31-60"), (61, 90, "61-90"), (91, np.inf, "91+")]
HORIZONS = [3, 6, 12, 24, 36]


# ---------- Lisboa ----------
def prepare_lisboa(d: pd.DataFrame) -> pd.DataFrame:
    d = d.copy()
    for c in ["EnrollmentStart", "EnrollmentFinish", "DateLastVisit"]:
        d[c] = pd.to_datetime(d[c])
    d["months"] = (d["EnrollmentFinish"] - d["EnrollmentStart"]).dt.days / DAYS_PER_MONTH
    d["event"] = d["Dropout"].astype(int)
    d["freq_band"] = pd.cut(d["AverageFrequency"], [b[0] for b in FREQ_BANDS] + [np.inf], right=False,
                            labels=[b[2] for b in FREQ_BANDS]).astype(str)
    d["renewals"] = d["NumberOfRenewals"].clip(upper=3).map({0: "0", 1: "1", 2: "2", 3: "3+"})
    d["recency_band"] = pd.cut(d["DaysWithoutFrequency"], [0, 7.5, 30.5, 60.5, 90.5, np.inf], right=False,
                               labels=[b[2] for b in RECENCY_BANDS]).astype(str)
    d["classes"] = np.where(d["AttendedClasses"] > 0, "Attended classes", "No classes")
    return d


def kaplan_meier(months: np.ndarray, event: np.ndarray) -> pd.DataFrame:
    """Product-limit estimate with Greenwood variance and log-log 95% interval."""
    t = np.asarray(months, float); e = np.asarray(event, int)
    times = np.unique(t[e == 1])
    order = np.argsort(t); t, e = t[order], e[order]
    s, var_sum, rows = 1.0, 0.0, []
    for u in times:
        n = int((t >= u).sum()); dth = int(((t == u) & (e == 1)).sum())
        s *= 1 - dth / n
        if n > dth:
            var_sum += dth / (n * (n - dth))
        rows.append((u, n, dth, s, var_sum))
    km = pd.DataFrame(rows, columns=["months", "at_risk", "events", "survival", "gw"])
    with np.errstate(divide="ignore", invalid="ignore"):
        se = np.sqrt(km["gw"]) / np.abs(np.log(km["survival"]))
        z = 1.959964
        km["lo"] = km["survival"] ** np.exp(z * se)
        km["hi"] = km["survival"] ** np.exp(-z * se)
    return km.drop(columns="gw")


def km_at(km: pd.DataFrame, m: float) -> dict:
    r = km[km["months"] <= m]
    if r.empty:
        return {"months": m, "survival": 1.0, "lo": 1.0, "hi": 1.0}
    r = r.iloc[-1]
    return {"months": m, "survival": float(r["survival"]), "lo": float(r["lo"]), "hi": float(r["hi"])}


def km_median(km: pd.DataFrame) -> float | None:
    r = km[km["survival"] <= 0.5]
    return float(r["months"].iloc[0]) if len(r) else None


def km_curve(km: pd.DataFrame, max_months: int = 48) -> list:
    return [round(km_at(km, m)["survival"], 4) for m in range(0, max_months + 1)]


def group_survival(d: pd.DataFrame, col: str, order: list) -> list:
    out = []
    for g in order:
        x = d[d[col] == g]
        km = kaplan_meier(x["months"], x["event"])
        out.append({"group": g, "users": int(len(x)), "dropouts": int(x["event"].sum()),
                    "dropout_share": float(x["event"].mean()), "median_months": km_median(km),
                    "s12": km_at(km, 12), "curve": km_curve(km)})
    return out


def lisboa(d: pd.DataFrame) -> dict:
    d = prepare_lisboa(d)
    km = kaplan_meier(d["months"], d["event"])
    act, out = d[d["event"] == 0], d[d["event"] == 1]
    rec = (d.groupby(["recency_band", "event"]).size().unstack(fill_value=0)
             .reindex([b[2] for b in RECENCY_BANDS]))
    return {
        "users": int(len(d)), "dropouts": int(d["event"].sum()), "dropout_share": float(d["event"].mean()),
        "active": int(len(act)),
        "enrol_first": str(d["EnrollmentStart"].min().date()), "enrol_last": str(d["EnrollmentStart"].max().date()),
        "censor_date": str(act["EnrollmentFinish"].max().date()),
        "median_months": km_median(km),
        "survival_at": [km_at(km, m) for m in HORIZONS],
        "curve": km_curve(km),
        "by_frequency": group_survival(d, "freq_band", [b[2] for b in FREQ_BANDS]),
        "by_renewals": group_survival(d, "renewals", ["0", "1", "2", "3+"]),
        "by_classes": group_survival(d, "classes", ["No classes", "Attended classes"]),
        "recency": {
            "median_days_dropouts": float(out["DaysWithoutFrequency"].median()),
            "median_days_active": float(act["DaysWithoutFrequency"].median()),
            "dropouts_over_30_days": float((out["DaysWithoutFrequency"] > 30).mean()),
            "active_over_30_days": float((act["DaysWithoutFrequency"] > 30).mean()),
            "bands": [{"band": b, "dropouts": int(rec.loc[b, 1]), "active": int(rec.loc[b, 0])} for b in rec.index],
        },
        "frequency_context": [{"group": g, "median_enrolment": str(x["EnrollmentStart"].median().date()),
                               "active_share": float(1 - x["event"].mean())}
                              for g in [b[2] for b in FREQ_BANDS] for x in [d[d["freq_band"] == g]]],
        "frequency_median": {"dropouts": float(out["AverageFrequency"].median()), "active": float(act["AverageFrequency"].median())},
    }


# ---------- Carrera ----------
def weekly_long(c: pd.DataFrame) -> pd.DataFrame:
    """Adjacent pre-study week pairs: visits in week k+1 before the study, then week k."""
    rows = []
    for k in range(8, 1, -1):
        rows.append(pd.DataFrame({"person": c.index, "now": c[f"previsits{k}"].to_numpy(), "next": c[f"previsits{k - 1}"].to_numpy()}))
    return pd.concat(rows, ignore_index=True)


def auc(score: np.ndarray, label: np.ndarray) -> float:
    s = pd.Series(score).rank().to_numpy(); y = np.asarray(label).astype(bool)
    n1, n0 = y.sum(), (~y).sum()
    return float((s[y].sum() - n1 * (n1 + 1) / 2) / (n1 * n0))


def carrera_stats(c: pd.DataFrame) -> dict:
    w = weekly_long(c)
    early = c[[f"previsits{i}" for i in range(5, 9)]].sum(axis=1)
    late = c["past4"]
    ctrl = c[c["treatment"] == "control"]
    any_now = w["now"] > 0
    return {
        "week_pairs": int(len(w)),
        "r_week_to_week": float(np.corrcoef(w["now"], w["next"])[0, 1]),
        "p_any_next_given_any": float((w.loc[any_now, "next"] > 0).mean()),
        "p_any_next_given_none": float((w.loc[~any_now, "next"] > 0).mean()),
        "r_weeks5_8_to_1_4": float(np.corrcoef(early, late)[0, 1]),
        "auc_any_weeks1_4": auc(early.to_numpy(), (late > 0).to_numpy()),
        "p_zero_late_given_zero_early": float((late[early == 0] == 0).mean()),
        "n_zero_early": int((early == 0).sum()),
        "control_n": int(len(ctrl)),
        "r_control_past4_to_study": float(np.corrcoef(ctrl["past4"], ctrl["visits"])[0, 1]),
        "r_control_past4_to_after": float(np.corrcoef(ctrl["past4"], ctrl["visits_next4weeks"])[0, 1]),
        "control_mean_past4": float(ctrl["past4"].mean()), "control_mean_study": float(ctrl["visits"].mean()),
        "control_mean_after": float(ctrl["visits_next4weeks"].mean()),
    }


def carrera(c: pd.DataFrame, n_boot: int = N_BOOT) -> dict:
    c = c.reset_index(drop=True)
    est = carrera_stats(c)
    rng = np.random.default_rng(SEED)
    keys = ["r_week_to_week", "p_any_next_given_any", "p_any_next_given_none", "r_weeks5_8_to_1_4",
            "auc_any_weeks1_4", "r_control_past4_to_study", "r_control_past4_to_after"]
    boot = {k: [] for k in keys}
    ctrl_idx = np.flatnonzero(c["treatment"].to_numpy() == "control")
    other_idx = np.flatnonzero(c["treatment"].to_numpy() != "control")
    for _ in range(n_boot):
        # Resample people within arm so the control group keeps its size.
        idx = np.concatenate([rng.choice(ctrl_idx, len(ctrl_idx)), rng.choice(other_idx, len(other_idx))])
        s = carrera_stats(c.iloc[idx].reset_index(drop=True))
        for k in keys:
            boot[k].append(s[k])
    est["ci"] = {k: [float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5))] for k, v in boot.items()}
    est["n_boot"] = n_boot
    w = weekly_long(c)
    tr = pd.crosstab(w["now"].clip(upper=4), w["next"].clip(upper=4))
    est["transition"] = {"rows": [str(i) if i < 4 else "4+" for i in tr.index], "cols": [str(i) if i < 4 else "4+" for i in tr.columns],
                         "counts": tr.to_numpy().tolist()}
    est["people"] = int(len(c))
    est["weekly_means"] = [float(c[f"previsits{k}"].mean()) for k in range(8, 0, -1)]
    return est


def run(lis: pd.DataFrame, car: pd.DataFrame, n_boot: int = N_BOOT) -> dict:
    return {"lisboa": lisboa(lis), "carrera": carrera(car, n_boot)}


def checks(r: dict) -> None:
    L, C = r["lisboa"], r["carrera"]
    assert L["users"] == 14942 and L["dropouts"] == 11968, "Lisboa totals must match the source and OGDT"
    assert abs(L["dropout_share"] - 0.8009637264087807) < 1e-12
    assert sum(g["users"] for g in L["by_frequency"]) == L["users"]
    assert C["people"] == 1292 and C["week_pairs"] == 1292 * 7
    for k, (lo, hi) in C["ci"].items():
        assert lo <= C[k] <= hi, k
