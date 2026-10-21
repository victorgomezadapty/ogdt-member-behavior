# Publication review — 20 October 2026

The [primary page](https://eml.berkeley.edu/~sdellavi/data/gymdata.shtml) was consulted again
and the `readme.txt` inside the hash-pinned ZIP was read. They explain access and variables but provide
no explicit redistribution license for the table. The website's copyright is not an open data
license. Result: redistribution rights are **not established**; CC0, CC BY or MIT is not inferred.
The authors were not contacted and no mirror dataset was published.

The Kaggle package contains our standalone notebook with attribution, selection policy,
hashes and limits. It downloads from the primary URL at run time or reads a file the user
authorizes. The ZIP is stored temporarily outside the outputs directory; the table and individual rows
stay in memory. Only aggregate JSON and a figure are saved. No sources, IDs, per-person derivatives,
Retention files, secrets or local paths are attached.

The MIT license of the original OGDT code does not change the rights of the data, the paper, the authors'
code or Mindweave (CC BY-NC 4.0). Those sources are not included in the Berkeley code package.

The [official Kaggle metadata documentation](https://github.com/Kaggle/kaggle-cli/blob/main/docs/kernels_metadata.md)
allows running notebooks with Internet access. Remote validation was first done privately. Run status,
environment and results are recorded in `reports/berkeley/kaggle_validation.json`. A successful run
verifies portability and results; it does not grant rights over the data or validate states, prediction or
intervention.

## Public release — 21 October 2026

The public step followed the same rule: **publish code and aggregates, never data**. Contacting the authors
for a data license is out of scope, so nothing beyond aggregates will be released.

- **Kaggle:** the notebook is public (version 2, COMPLETE, totals identical to the local run). It still downloads
  the author archive at run time and writes aggregates only.
- **GitHub:** the public repository holds code, documentation, the data contract and four aggregate figures.
  Raw data and person-level derivatives are ignored by Git. The individual-trajectories figure and the local
  HTML report that embeds it stay local; `report.md` names that figure without including it.
- **Site:** <https://ogdt-member-behavior.vercel.app> is built by `scripts/build_site.py` from aggregates only.
  It refuses any group below 50 member-months and contains no member IDs or rows. The same aggregate tables are
  offered as CSV downloads.
