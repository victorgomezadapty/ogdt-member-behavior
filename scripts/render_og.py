"""Render site/og.html to site/assets/og.png (1200x630) with headless Chrome or Edge."""
from pathlib import Path
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
CANDIDATES = [
    shutil.which("chrome"), shutil.which("google-chrome"), shutil.which("msedge"),
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
]


def main():
    browser = next((c for c in CANDIDATES if c and Path(c).exists()), None)
    if not browser:
        raise SystemExit("No Chrome or Edge found for headless rendering")
    out = ROOT / "site/assets/og.png"
    with tempfile.TemporaryDirectory() as profile:
        subprocess.run([browser, "--headless=new", "--disable-gpu", "--hide-scrollbars", f"--user-data-dir={profile}",
                        "--window-size=1200,630", "--virtual-time-budget=5000", f"--screenshot={out}",
                        (ROOT / "site/og.html").as_uri()], check=True, capture_output=True)
    print(f"Wrote {out.relative_to(ROOT)}: {out.stat().st_size:,} bytes")


if __name__ == "__main__":
    main()
