"""Download the two open sources and check their hashes.

Lisboa Sport Services Dataset (Pinheiro & Cavique), Mendeley Data v1, CC BY 4.0
  https://data.mendeley.com/datasets/yprk4jdgnv/1  -> data/raw/lisboa/DadosV3.csv
Carrera, Royer, Stehr, Sydnor, Sial & Taubinsky, replication package for
"Who Chooses Commitment? Evidence and Welfare Implications", Zenodo 5173081.
  The package's LICENSE.txt dedicates the data to CC0 1.0 (code: BSD-3-Clause);
  the Zenodo record lists CC BY 4.0. Either way it is attributed here.
  https://doi.org/10.5281/zenodo.5173081 -> data/raw/carrera/cleaned_commitment_study_data.dta
"""
from __future__ import annotations

import hashlib
import io
import json
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LISBOA = ROOT / "data" / "raw" / "lisboa" / "DadosV3.csv"
CARRERA = ROOT / "data" / "raw" / "carrera" / "cleaned_commitment_study_data.dta"
LISBOA_SHA256 = "775f226bef749497017579a9088e5f83249d8f1916c27d8d89acc189bccaa04d"
CARRERA_ZIP_MD5 = "92845f0f1f09893fc2e4fd41192bf439"
MENDELEY_API = "https://data.mendeley.com/public-api/datasets/yprk4jdgnv/files?folder_id=root&version=1"
ZENODO_ZIP = "https://zenodo.org/api/records/5173081/files/Who_Chooses_Commitment_Replication.zip/content"


def get(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req) as r:
        return r.read()


def main() -> None:
    LISBOA.parent.mkdir(parents=True, exist_ok=True)
    CARRERA.parent.mkdir(parents=True, exist_ok=True)
    if not LISBOA.exists():
        files = json.loads(get(MENDELEY_API))
        f = next(x for x in files if x["filename"] == "DadosV3.csv")
        LISBOA.write_bytes(get(f["content_details"]["download_url"]))
    sha = hashlib.sha256(LISBOA.read_bytes()).hexdigest()
    assert sha == LISBOA_SHA256, f"Lisboa hash mismatch: {sha}"
    if not CARRERA.exists():
        z = get(ZENODO_ZIP)
        assert hashlib.md5(z).hexdigest() == CARRERA_ZIP_MD5, "Zenodo zip hash mismatch"
        with zipfile.ZipFile(io.BytesIO(z)) as zf:
            name = next(n for n in zf.namelist() if n.endswith("Data/cleaned_commitment_study_data.dta"))
            CARRERA.write_bytes(zf.read(name))
    manifest = {
        "lisboa": {"path": "data/raw/lisboa/DadosV3.csv", "sha256": sha, "source": "https://data.mendeley.com/datasets/yprk4jdgnv/1", "license": "CC BY 4.0"},
        "carrera": {"path": "data/raw/carrera/cleaned_commitment_study_data.dta",
                    "sha256": hashlib.sha256(CARRERA.read_bytes()).hexdigest(),
                    "source": "https://doi.org/10.5281/zenodo.5173081", "license": "CC0 1.0 (package LICENSE.txt); Zenodo record: CC BY 4.0"},
    }
    (ROOT / "data" / "source_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
