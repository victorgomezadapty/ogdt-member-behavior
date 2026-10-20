"""Execute observation notebooks using this interpreter, preserving outputs."""
from pathlib import Path
import json
import sys
import argparse
import nbformat
from nbclient import NotebookClient
from jupyter_client.kernelspec import KernelSpecManager

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser()
    available = ["01_data_understanding.ipynb", "02_member_attendance_eda.ipynb", "03_temporal_behavior.ipynb", "03b_longitudinal_eda.ipynb", "07_berkeley_monthly_eda.ipynb"]
    parser.add_argument("--notebook", choices=available)
    args = parser.parse_args()
    # A workspace-local kernelspec ensures replay uses the tested interpreter.
    spec_dir = ROOT / "reports/runtime-kernels/ogdt-python"
    spec_dir.mkdir(parents=True, exist_ok=True)
    (spec_dir / "kernel.json").write_text(json.dumps({"argv": [sys.executable, "-m", "ipykernel_launcher", "-f", "{connection_file}"], "display_name": "OGDT Python", "language": "python"}), encoding="utf-8")
    ksm = KernelSpecManager(kernel_dirs=[str(spec_dir.parent)])
    results = []
    # Preserve the existing synthetic rebuild default; real monthly replay is explicit.
    paths = [ROOT / "notebooks" / args.notebook] if args.notebook else [ROOT / "notebooks" / name for name in available[:4] if (ROOT / "notebooks" / name).exists()]
    for path in paths:
        nb = nbformat.read(path, as_version=4)
        client = NotebookClient(nb, timeout=120, kernel_name="ogdt-python", resources={"metadata": {"path": str(ROOT)}})
        client.create_kernel_manager()
        client.km.kernel_spec_manager = ksm
        client.execute()
        nbformat.write(nb, path)
        results.append({"notebook": path.name, "executed_code_cells": sum(c.cell_type == "code" for c in nb.cells), "errors": sum(o.output_type == "error" for c in nb.cells if c.cell_type == "code" for o in c.outputs)})
        print(f"Executed {path.name}", flush=True)
    output_path = ROOT / "reports/notebook_execution.json"
    previous = json.loads(output_path.read_text(encoding="utf-8")) if output_path.exists() and args.notebook else []
    merged = {r["notebook"]: r for r in previous + results}
    output_path.write_text(json.dumps(list(merged.values()), indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
