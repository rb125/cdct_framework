"""
Re-runs jury experiments only for result files with empty performance data.
"""
import json
import glob
import subprocess
import sys
from pathlib import Path

results_dir = Path("results_jury")
concepts_dir = Path("concepts")

# Build a map from concept name -> concept file
concept_map = {f.stem: str(f) for f in concepts_dir.glob("*.json")}

failed_files = []
for f in sorted(results_dir.glob("*.json")):
    d = json.load(open(f))
    if not d.get("performance"):
        failed_files.append((d.get("subject_model"), d.get("concept"), f))

print(f"Found {len(failed_files)} result files with empty performance. Re-running...\n")

completed, failed = 0, 0
for model, concept, result_path in failed_files:
    # Find matching concept file (concept field may be partial, e.g. "f_equals_ma")
    concept_file = next(
        (v for k, v in concept_map.items() if concept in k or k.endswith(concept)),
        None
    )
    if not concept_file:
        print(f"  [SKIP] No concept file found for concept='{concept}' (model={model})")
        continue

    print(f"  Running: {model} × {concept}")
    cmd = [sys.executable, "main_jury.py", "--concept", concept_file, "--model", model]
    try:
        subprocess.run(cmd, check=True)
        completed += 1
        print(f"  ✓ Done: {model} × {concept}")
    except subprocess.CalledProcessError as e:
        failed += 1
        print(f"  ✗ Failed: {model} × {concept} — {e}")

print(f"\nDone. Completed: {completed}, Failed: {failed}")
