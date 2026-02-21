import subprocess
import sys
import os
from pathlib import Path

def run_command(cmd, description):
    """Run a shell command and handle output/errors."""
    print(f"
>>> {description}")
    print(f"Running: {' '.join(cmd)}")
    try:
        # Use sys.executable to ensure we use the same python environment
        subprocess.run(cmd, check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"
❌ Error during: {description}")
        print(f"Command failed with exit code {e.returncode}")
        return False
    except KeyboardInterrupt:
        print(f"

🛑 Execution interrupted by user.")
        sys.exit(0)

def main():
    """
    Simplified entry point for the full CDCT evaluation.
    This script runs the entire pipeline:
    1. Subject model experiments (with skipping)
    2. Jury evaluations (with skipping)
    3. Metric calculation (CSV export)
    4. Comprehensive analysis (JSON report)
    """
    print("=" * 80)
    print("CDCT FULL EVALUATION AUTOMATION")
    print("=" * 80)
    print("This script will run the entire CDCT pipeline.")
    print("Models and concepts already evaluated will be automatically skipped.")
    print("=" * 80)

    # 1. Subject Evaluations
    if not run_command(
        [sys.executable, "run_all.py", "--models-list", "subject"],
        "Phase 1: Subject Model Evaluations (Experimentation)"
    ):
        print("Stopping due to errors in Phase 1.")
        sys.exit(1)

    # 2. Jury Evaluations
    if not run_command(
        [sys.executable, "run_all_jury_smart.py"],
        "Phase 2: Jury Evaluations (Smart Skipping)"
    ):
        print("Stopping due to errors in Phase 2.")
        sys.exit(1)

    # 3. Calculate Metrics
    if not run_command(
        [sys.executable, "calculate_cdct_metrics.py"],
        "Phase 3: Calculating CDCT Metrics (SF, CRI, HOC, CI)"
    ):
        print("Warning: Metric calculation encountered issues.")

    # 4. Comprehensive Analysis
    if not run_command(
        [sys.executable, "analyze_jury_results.py"],
        "Phase 4: Comprehensive Jury Analysis (Fleiss' Kappa, etc.)"
    ):
        print("Warning: Final analysis encountered issues.")

    print("
" + "=" * 80)
    print("🎉 FULL CDCT EVALUATION PIPELINE COMPLETE")
    print("=" * 80)
    print("Results are available in:")
    print("  - results/          (Subject raw results)")
    print("  - results_jury/     (Jury raw results)")
    print("  - export/           (Final CSV metrics)")
    print("  - verification_results/ (Summary analysis reports)")
    print("=" * 80)

if __name__ == "__main__":
    main()
