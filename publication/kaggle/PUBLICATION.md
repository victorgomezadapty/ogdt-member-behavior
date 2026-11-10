# Kaggle publication steps (manual)

1. Run `python scripts/prepare.py`; it writes `publication/kaggle/dataset/lisboa_members.csv` and `carrera_weekly_visits.csv`.
2. Create the dataset `vctorandrsgmezlpez/open-gym-member-behavior-inputs` from `publication/kaggle/dataset/` (metadata in `dataset-metadata.json`, licence CC BY 4.0, attribution to both sources).
3. Push the notebook from `publication/kaggle/` (`kernel-metadata.json`, internet off, the dataset above attached). The kernel keeps its existing id, so its URL is unchanged.
4. Check the run log: `Users 14,942, dropouts 11,968 (80.1%), censored 2,974 at 2019-10-31` and no errors.
5. Remove any older dataset sources from the kernel settings if Kaggle keeps them.
