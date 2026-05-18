"""
Download IFEval, analyze instruction type distribution, produce stratified sample of 200 prompts.
Then test constraint-preserving compression on 15 sample prompts.
"""
import json
from collections import Counter
from datasets import load_dataset

def main():
    ds = load_dataset("google/IFEval", split="train")
    print(f"Total IFEval prompts: {len(ds)}")

    # Analyze instruction type distribution
    type_counter = Counter()
    for row in ds:
        for iid in row["instruction_id_list"]:
            type_counter[iid] += 1

    print(f"\n=== Instruction Types ({len(type_counter)} unique) ===")
    for itype, count in type_counter.most_common():
        print(f"  {itype}: {count}")

    # Group prompts by their PRIMARY instruction type (first in list)
    by_primary_type = {}
    for i, row in enumerate(ds):
        primary = row["instruction_id_list"][0]
        if primary not in by_primary_type:
            by_primary_type[primary] = []
        by_primary_type[primary].append(i)

    print(f"\n=== Primary Instruction Types ({len(by_primary_type)}) ===")
    for ptype, indices in sorted(by_primary_type.items(), key=lambda x: -len(x[1])):
        print(f"  {ptype}: {len(indices)} prompts")

    # Stratified sample: ~200 prompts, proportional to type frequency
    # Minimum 3 per type, cap at 15 per type
    target = 200
    sample_indices = []
    total_available = sum(len(v) for v in by_primary_type.values())

    for ptype, indices in sorted(by_primary_type.items()):
        # Proportional allocation with min=3, max=15
        proportion = len(indices) / total_available
        n = max(3, min(15, round(proportion * target)))
        selected = indices[:n]
        sample_indices.extend(selected)

    # Trim to ~200 if over
    sample_indices = sample_indices[:200]
    print(f"\n=== Stratified Sample: {len(sample_indices)} prompts ===")

    # Build sample dataset
    sample = []
    for idx in sample_indices:
        row = ds[idx]
        sample.append({
            "key": row["key"],
            "prompt": row["prompt"],
            "instruction_id_list": row["instruction_id_list"],
            "kwargs": row["kwargs"],
        })

    # Verify type coverage
    sample_types = Counter()
    for s in sample:
        for iid in s["instruction_id_list"]:
            sample_types[iid] += 1
    print(f"Types covered in sample: {len(sample_types)}/{len(type_counter)}")

    # Save
    with open("ifeval_sample_200.json", "w") as f:
        json.dump(sample, f, indent=2)
    print(f"\n✓ Saved {len(sample)} prompts to ifeval_sample_200.json")

    # Print 15 example prompts for manual compression testing
    print("\n\n=== 15 SAMPLE PROMPTS FOR COMPRESSION TESTING ===")
    # Pick diverse ones
    test_indices = [0, 10, 20, 30, 50, 70, 90, 110, 130, 140, 150, 160, 170, 180, 190]
    test_prompts = []
    for i in test_indices[:15]:
        if i < len(sample):
            p = sample[i]
            print(f"\n--- Prompt {i} (key={p['key']}) ---")
            print(f"  Types: {p['instruction_id_list']}")
            print(f"  Text: {p['prompt'][:200]}...")
            test_prompts.append(p)

    with open("ifeval_compression_test_15.json", "w") as f:
        json.dump(test_prompts, f, indent=2)
    print(f"\n✓ Saved 15 test prompts to ifeval_compression_test_15.json")

if __name__ == "__main__":
    main()
