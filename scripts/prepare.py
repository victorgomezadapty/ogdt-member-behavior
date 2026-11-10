"""Write the two analysis inputs used by the pipeline and by the Kaggle notebook.

- data/processed/lisboa_members.csv: the Lisboa file with only the columns analysed
  (no Id, age or gender), CC BY 4.0.
- data/processed/carrera_weekly_visits.csv: pre-study weekly visits and study-period
  totals from the Carrera et al. replication data (CC0), no demographics.
Both are also copied to publication/kaggle/dataset/ for upload.
"""
from __future__ import annotations

import shutil
from pathlib import Path

import pandas as pd
import pyreadstat

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
OUT = ROOT / "data" / "processed"
KAGGLE = ROOT / "publication" / "kaggle" / "dataset"

LISBOA_COLS = ["EnrollmentStart", "EnrollmentFinish", "EnrollmentDuration", "DateLastVisit", "DaysWithoutFrequency",
               "AverageFrequency", "NumberOfFrequencies", "AttendedClasses", "NumberOfRenewals", "Dropout"]
CARRERA_COLS = ["wave", "treatment", *[f"previsits{i}" for i in range(1, 9)], "past4", "visits", "visits_next4weeks", "visits_100days"]


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    KAGGLE.mkdir(parents=True, exist_ok=True)
    lis = pd.read_csv(RAW / "lisboa" / "DadosV3.csv", sep=";")[LISBOA_COLS]
    lis.to_csv(OUT / "lisboa_members.csv", index=False)
    car, _ = pyreadstat.read_dta(str(RAW / "carrera" / "cleaned_commitment_study_data.dta"))
    car = car[CARRERA_COLS].copy()
    for c in CARRERA_COLS[2:]:
        car[c] = car[c].astype(int)
    car.to_csv(OUT / "carrera_weekly_visits.csv", index=False)
    for name in ["lisboa_members.csv", "carrera_weekly_visits.csv"]:
        shutil.copyfile(OUT / name, KAGGLE / name)
    print(lis.shape, car.shape)


if __name__ == "__main__":
    main()
