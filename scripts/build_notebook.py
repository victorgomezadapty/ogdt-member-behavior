"""Build the analysis notebook, execute it locally and write the Kaggle copy.

The notebook inlines src/analysis.py so it runs offline on Kaggle with only the two
attached input files:
  lisboa_members.csv          (Sport Services Dataset, Pinheiro & Cavique, CC BY 4.0)
  carrera_weekly_visits.csv   (Carrera et al. replication data, CC0 1.0)
"""
from __future__ import annotations

import copy
import json
from pathlib import Path

import nbformat
from nbclient import NotebookClient

ROOT = Path(__file__).resolve().parents[1]
md, code = nbformat.v4.new_markdown_cell, nbformat.v4.new_code_cell


def cells() -> list:
    analysis_src = (ROOT / "src" / "analysis.py").read_text(encoding="utf-8")
    return [
        md("# OGDT Member Behavior: how members use the gym before they stop\n\n"
           "Part of **Open Gym Digital Twin** (Observe module). This notebook describes membership length, renewals, "
           "visit frequency, classes and recency for 14,942 users of a sports facility, and the week-to-week persistence "
           "of gym visits for 1,292 members of a US gym. It describes behavior; it does not predict dropout.\n\n"
           "## Exact inputs\n\n"
           "| File | Rows | Source | Licence |\n|---|---|---|---|\n"
           "| `lisboa_members.csv` | 14,942 | Pinheiro, P. & Cavique, L. (2020). Sport Services Dataset, Mendeley Data v1, doi:10.17632/yprk4jdgnv.1. Columns kept: enrolment dates and length, last visit, days without a visit, average weekly frequency, visits, classes, renewals, dropout. | CC BY 4.0 |\n"
           "| `carrera_weekly_visits.csv` | 1,292 | Carrera, Royer, Stehr, Sydnor & Taubinsky, *Who Chooses Commitment?*, Review of Economic Studies, doi:10.1093/restud/rdab056; replication data on Zenodo, doi:10.5281/zenodo.5173081. Columns kept: wave, treatment, weekly visits 1 to 8 weeks before the study, visits in the 4 weeks before, during and after. | CC0 1.0 (package licence file) |\n\n"
           "Both files are attached as the Kaggle dataset `vctorandrsgmezlpez/open-gym-member-behavior-inputs`. No internet access is needed."),
        code("from pathlib import Path\nimport json\nimport numpy as np\nimport pandas as pd\nimport matplotlib.pyplot as plt\n\n"
             "def find(name):\n"
             "    for base in [Path('/kaggle/input'), Path('../data/processed'), Path('data/processed')]:\n"
             "        hits = sorted(base.glob('**/' + name)) if base.exists() else []\n"
             "        if hits:\n            return hits[0]\n"
             "    raise FileNotFoundError(name)\n\n"
             "LISBOA, CARRERA = find('lisboa_members.csv'), find('carrera_weekly_visits.csv')\n"
             "lis, car = pd.read_csv(LISBOA), pd.read_csv(CARRERA)\nprint(LISBOA, lis.shape)\nprint(CARRERA, car.shape)"),
        md("## Analysis code\n\nThe same module the website build uses (`src/analysis.py`), inlined so the notebook is self-contained."),
        code(analysis_src),
        code("res = run(lis, car)\nchecks(res)\nL, C = res['lisboa'], res['carrera']\n"
             "print(f\"Users {L['users']:,}, dropouts {L['dropouts']:,} ({L['dropout_share']:.1%}), censored {L['active']:,} at {L['censor_date']}\")"),
        md("## 1. Membership length (Kaplan-Meier)\n\nUsers still active at extraction are censored, not counted as dropouts."),
        code("print('Median membership, months:', round(L['median_months'], 1))\n"
             "display(pd.DataFrame(L['survival_at']).round(3))\n"
             "fig, ax = plt.subplots(figsize=(8, 3.5))\nax.step(range(49), L['curve'], where='post', color='#c8372d')\n"
             "ax.set(xlabel='Months since enrolment', ylabel='Share still active', ylim=(0, 1.02)); ax.grid(alpha=.3); plt.show()"),
        md("## 2. Renewals, weekly frequency and classes\n\nAll three are measured over the whole membership, so they describe how memberships unfolded. "
           "Renewals are mechanically tied to length."),
        code("def tbl(key):\n    return pd.DataFrame([{**{k: g[k] for k in ['group', 'users', 'dropouts', 'dropout_share', 'median_months']}, 'survival_12m': g['s12']['survival'], 'ci_low': g['s12']['lo'], 'ci_high': g['s12']['hi']} for g in L[key]]).round(3)\n"
             "for key in ['by_renewals', 'by_frequency', 'by_classes']:\n    print(key); display(tbl(key))\n"
             "display(pd.DataFrame(L['frequency_context']).round(3))\n"
             "fig, axes = plt.subplots(1, 3, figsize=(14, 3.5), sharey=True)\n"
             "for ax, key in zip(axes, ['by_renewals', 'by_frequency', 'by_classes']):\n"
             "    for g in L[key]:\n        ax.step(range(49), g['curve'], where='post', label=f\"{g['group']} (n={g['users']:,})\")\n"
             "    ax.set(title=key.replace('_', ' '), xlabel='Months'); ax.legend(fontsize=8); ax.grid(alpha=.3)\nplt.show()"),
        md("## 3. Days without a visit at the end of the record\n\nFor dropouts this is measured at the dropout date. Descriptive only."),
        code("rec = L['recency']\nprint({k: v for k, v in rec.items() if k != 'bands'})\n"
             "b = pd.DataFrame(rec['bands']).set_index('band')\ndisplay((b / b.sum()).round(3).assign(dropouts_n=b['dropouts'], active_n=b['active']))"),
        md("## 4. Weekly persistence (Carrera et al.)\n\nPre-study weeks only (no intervention yet), plus the control group for the study and follow-up periods. "
           "Intervals: 1,000 person-level bootstrap resamples, seed 20261110."),
        code("keys = ['r_week_to_week', 'p_any_next_given_any', 'p_any_next_given_none', 'r_weeks5_8_to_1_4', 'auc_any_weeks1_4', 'r_control_past4_to_study', 'r_control_past4_to_after']\n"
             "display(pd.DataFrame({'estimate': [C[k] for k in keys], 'ci_low': [C['ci'][k][0] for k in keys], 'ci_high': [C['ci'][k][1] for k in keys]}, index=keys).round(3))\n"
             "tr = pd.DataFrame(C['transition']['counts'], index=C['transition']['rows'], columns=C['transition']['cols'])\n"
             "display((tr.div(tr.sum(axis=1), axis=0)).round(3))\n"
             "print('Control group means, before / during / after:', round(C['control_mean_past4'], 2), round(C['control_mean_study'], 2), round(C['control_mean_after'], 2))"),
        md("## What this does not show\n\n"
           "- No causal effect of classes, renewals or frequency on staying.\n"
           "- No early warning: Lisbon measures are taken over or at the end of each membership.\n"
           "- **Dropped:** the earlier monthly contract-transition analysis. No openly licensed dataset records gym contracts month by month, so it was removed rather than replaced with synthetic data.\n"
           "- One facility and one gym study; neither represents every gym.\n\n"
           "Code: https://github.com/victorgomezadapty/ogdt-member-behavior · Site: https://ogdt-member-behavior.vercel.app"),
    ]


def main() -> None:
    nb = nbformat.v4.new_notebook(cells=cells())
    nb.metadata["kernelspec"] = {"name": "python3", "display_name": "Python 3", "language": "python"}
    clean = copy.deepcopy(nb)
    (ROOT / "notebooks").mkdir(exist_ok=True)
    NotebookClient(nb, timeout=600, kernel_name="python3", resources={"metadata": {"path": str(ROOT / "notebooks")}}).execute()
    nbformat.write(nb, ROOT / "notebooks" / "member_behavior.ipynb")
    nbformat.write(clean, ROOT / "publication" / "kaggle" / "ogdt-member-behavior.ipynb")
    outs = [o.get("text", "") for c in nb.cells if c.cell_type == "code" for o in c.get("outputs", []) if o.get("output_type") == "stream"]
    print("executed;", next((o for o in outs if "Users" in o), "").strip())


if __name__ == "__main__":
    main()
