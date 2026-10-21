"""Freeze the author archive: copy Retention's verified copy, or download it from the author.

Never mutates the Retention lab. Either path must match the pinned archive hash.
"""
from pathlib import Path
import argparse
import hashlib
import json
import sys
import urllib.request
import zipfile
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.data.berkeley import DATASET_ID, ARCHIVE_SHA256, TABLE_SHA256


AUTHOR_ARCHIVE_URL = "https://eml.berkeley.edu/~sdellavi/data/data.zip"


def download_author_archive():
    request = urllib.request.Request(AUTHOR_ARCHIVE_URL, headers={"User-Agent": "OGDT-research/1.0"})
    with urllib.request.urlopen(request, timeout=90) as response:
        return response.read()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=ROOT.parent / "ogdt-retention/data/raw/berkeley/data.zip")
    parser.add_argument("--download", action="store_true",
                        help="download the archive from the author's page instead of copying a local file")
    args = parser.parse_args()
    source = AUTHOR_ARCHIVE_URL if args.download else args.source.resolve()
    content = download_author_archive() if args.download else source.read_bytes()
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
                "local_acquisition": ("downloaded from author page" if args.download
                                      else "byte-identical copy of author archive held in ogdt-retention"),
                "copied_from": str(source), "acquired_at_utc": datetime.now(timezone.utc).isoformat(),
                "archive_sha256": ARCHIVE_SHA256, "archive_bytes": len(content), "files": files,
                "redistribution_terms": "pending_review_no_raw_or_person_level_publication"}
    (raw / "manifest.json").write_text(json.dumps(manifest, indent=2)+"\n", encoding="utf-8")
    print(f"Frozen Berkeley source: {len(content):,} bytes; hashes verified")


if __name__ == "__main__":
    main()
