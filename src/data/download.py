"""Download all substantive public tables at a pinned Hugging Face revision."""
from pathlib import Path
import argparse
import hashlib
import json
from datetime import datetime, timezone
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[2]
DATASET = "mindweave/gym-memberships"
REVISION = "3ff8e2fd4b429b5d0d4faf79344b3c23bc00fe5e"


def download(revision=REVISION):
    raw = ROOT / "data/raw"
    raw.mkdir(parents=True, exist_ok=True)
    files = ["README.md", "data/checkins.csv", "data/members.csv",
             "data/locations.csv", "data/plans.csv"]
    manifest = {"dataset": DATASET, "revision": revision, "synthetic": True,
                "license": "CC-BY-NC-4.0", "scope": "public free sample",
                "retrieved_at_utc": datetime.now(timezone.utc).isoformat(), "files": []}
    for name in files:
        url = f"https://huggingface.co/datasets/{DATASET}/resolve/{revision}/{name}"
        body = urlopen(url, timeout=60).read()
        target = raw / ("dataset_card.md" if name == "README.md" else Path(name).name)
        target.write_bytes(body)
        manifest["files"].append({"source_path": name, "local_path": target.name,
                                  "url": url, "bytes": len(body),
                                  "sha256": hashlib.sha256(body).hexdigest()})
    (raw / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"Downloaded {len(files)} files at {revision}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--revision", default=REVISION)
    download(parser.parse_args().revision)
