"""
Batch runner for CDCT experiments.
Iterates over all concept JSON files and runs experiments for each.
Skips already processed concepts.
"""

import os
import subprocess
import argparse
from pathlib import Path

def parse_args():
    parser = argparse.ArgumentParser(
        description="Run CDCT experiments for all concepts",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_all.py --model gpt-5-mini --deployment "gpt-5-mini"
  python run_all.py --model phi-4-mini-instruct --deployment "phi-4-mini-instruct"
        """
    )
    parser.add_argument("--model", type=str, required=True,
                        help="Name of the model (e.g., gpt-5-mini, phi-4-mini-instruct)")
    parser.add_argument("--deployment", type=str, required=True,
                        help="Deployment name for Azure (same as used in main.py)")
    parser.add_argument("--concepts-dir", type=str, default="concepts",
                        help="Directory containing concept JSON files")
    parser.add_argument("--results-dir", type=str, default="results",
                        help="Directory to store experiment results")
    parser.add_argument("--prompt-strategy", type=str, default="compression_aware",
                        help="Prompting strategy to use")
    parser.add_argument("--evaluation-mode", type=str, default="balanced",
                        help="Evaluation mode (strict | balanced | lenient)")
    parser.add_argument("--quiet", action="store_true",
                        help="Suppress verbose output from main.py")
    return parser.parse_args()

def already_done(concept_name: str, model: str, results_dir: Path) -> bool:
    """Check if results already exist for a given concept + model."""
    pattern = f"results_{concept_name}_{model.replace('/', '_')}_"
    for file in results_dir.iterdir():
        if file.name.startswith(pattern) and file.name.endswith(".json"):
            return True
    return False

def run_concept(concept_path: Path, args):
    """Run main.py for a single concept."""
    concept_name = concept_path.stem
    if already_done(concept_name, args.model, Path(args.results_dir)):
        print(f"✅ Skipping {concept_name} — already has results.")
        return
    
    print(f"\n🚀 Running experiment for: {concept_name}")
    cmd = [
        "python", "main.py",
        "--concept", str(concept_path),
        "--model", args.model,
        "--deployment", args.deployment,
        "--prompt-strategy", args.prompt_strategy,
        "--evaluation-mode", args.evaluation_mode,
        "--output-dir", args.results_dir,
    ]
    if args.quiet:
        cmd.append("--quiet")

    try:
        subprocess.run(cmd, check=True)
        print(f"✅ Completed: {concept_name}")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running {concept_name}: {e}")

def main():
    args = parse_args()

    concepts_dir = Path(args.concepts_dir)
    results_dir = Path(args.results_dir)
    results_dir.mkdir(exist_ok=True)

    concept_files = sorted(concepts_dir.glob("*.json"))
    if not concept_files:
        print("No concept files found.")
        return

    print(f"\nFound {len(concept_files)} concept files.")
    print(f"Model: {args.model} | Deployment: {args.deployment}")
    print("=" * 70)

    for concept_path in concept_files:
        run_concept(concept_path, args)

    print("\n🎉 All experiments complete!")

if __name__ == "__main__":
    main()

