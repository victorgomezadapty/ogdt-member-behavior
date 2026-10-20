"""Build a local overview for final figure inspection."""
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
paths = sorted((ROOT / "reports/figures").glob("*.png"))
fig, axes = plt.subplots(4, 3, figsize=(18, 20))
for ax, path in zip(axes.flat, paths):
    ax.imshow(plt.imread(path))
    ax.set_title(path.name, fontsize=9)
    ax.axis("off")
for ax in list(axes.flat)[len(paths):]:
    ax.axis("off")
fig.tight_layout()
fig.savefig(ROOT / "reports/visual_qa.png", dpi=140)
plt.close(fig)
