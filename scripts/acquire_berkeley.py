"""Freeze the author archive already acquired by Retention; never mutate that lab."""
from pathlib import Path
import argparse
import hashlib
import json
import sys
import zipfile
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.data.berkeley import DATASET_ID, ARCHIVE_SHA256, TABLE_SHA256


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=ROOT.parent / "ogdt-retention/data/raw/berkeley/data.zip")
    source = parser.parse_args().source.resolve()
    content = source.read_bytes()
    if hashlib.sha256(content).hexdigest() != ARCHIVE_SHA256:
        raise ValueError("Unexpected archive; reassess source before acquisition")
    raw = ROOT / "data/raw/berkeley"
    raw.mkdir(parents=True, exist_ok=True)
    target = raw / "data.zip"
    if target.exists() and hashlib.sha256(target.read_bytes()).hexdigest() != ARCHIVE_SHA256:
        raise ValueError("Refusing to overwrite a different local source")
    target.write_bytes(content)
    files = []
    with zipfile.ZipFile(target) as archive:
        for name in ["GymAERSourceData.dta", "readme.txt", "DataGymAERMar06.do"]:
            data = archive.read(name)
            files.append({"archive_member": name, "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()})
    if files[0]["sha256"] != TABLE_SHA256:
        raise ValueError("Unexpected source table")
    manifest = {"dataset_id": DATASET_ID, "synthetic": False, "source_page": "https://eml.berkeley.edu/~sdellavi/data/gymdata.shtml",
                "local_acquisition": "byte-identical copy of author archive held in ogdt-retention",
                "copied_from": str(source), "acquired_at_utc": datetime.now(timezone.utc).isoformat(),
                "archive_sha256": ARCHIVE_SHA256, "archive_bytes": len(content), "files": files,
                "redistribution_terms": "pending_review_no_raw_or_person_level_publication"}
    (raw / "manifest.json").write_text(json.dumps(manifest, indent=2)+"\n", encoding="utf-8")
    print(f"Frozen Berkeley source: {len(content):,} bytes; hashes verified")


if __name__ == "__main__":
    main()
