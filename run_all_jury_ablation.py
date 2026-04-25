"""
Batch run jury ablation (no_helpfulness) on all concepts and all subject models
"""
import os
import glob
import subprocess
import sys

from models_config import SUBJECT_MODELS_CONFIG

concepts = sorted(glob.glob(os.path.join("concepts", "*.json")))
models = [c["model_name"] for c in SUBJECT_MODELS_CONFIG]
output_dir = "results_jury_ablation"
os.makedirs(output_dir, exist_ok=True)

total = len(concepts) * len(models)
print(f"\n{'='*70}")
print(f"ABLATION STUDY: no_helpfulness — {len(models)} models × {len(concepts)} concepts")
print(f"Total runs: {total}")
print(f"{'='*70}\n")

completed, failed = 0, 0
for concept in concepts:
    cname = os.path.splitext(os.path.basename(concept))[0]
    for model in models:
        completed += 1
        print(f"\n[{completed}/{total}] {cname} × {model}")
        print("-" * 70)
        cmd = [
            sys.executable, "main_jury.py",
            "--concept", concept,
            "--model", model,
            "--ablation-type", "no_helpfulness",
            "--output-dir", output_dir,
        ]
        try:
            subprocess.run(cmd, check=True, capture_output=False)
            print(f"✓ {cname} × {model}")
        except subprocess.CalledProcessError:
            failed += 1
            print(f"✗ {cname} × {model}")

print(f"\n{'='*70}")
print(f"ABLATION COMPLETE: {completed - failed}/{total} succeeded, {failed} failed")
print(f"Results in: {output_dir}/")
print(f"{'='*70}\n")
