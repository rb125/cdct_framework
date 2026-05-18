"""Characterize MiniMax and grok anomalies quantitatively."""
import json
from pathlib import Path

RESULTS_DIR = Path("results_jury")
ABLATION_DIR = Path("results_jury_ablation")

def load_all(directory):
    results = []
    for f in sorted(directory.glob("*.json")):
        with open(f) as fh:
            results.append(json.load(fh))
    return results

def main():
    baseline = load_all(RESULTS_DIR)
    ablation = load_all(ABLATION_DIR)

    report = {"minimax": {"baseline_cl05": [], "ablation_cl05": []}, "grok": {"cl00_responses": []}}

    for r in baseline:
        model = r["subject_model"]
        concept = r["concept"]
        
        for p in r["performance"]:
            cl = p["compression_level"]
            
            # MiniMax at CL=0.5
            if "MiniMax" in model and abs(cl - 0.5) < 0.01:
                resp = p["response"]
                is_json_dump = "reasoningContent" in resp or resp.strip().startswith("[{")
                report["minimax"]["baseline_cl05"].append({
                    "concept": concept,
                    "response_length": p["response_length"],
                    "is_json_dump": is_json_dump,
                    "cc": p["jury_evaluation"]["consensus"]["CC"],
                    "sa": p["jury_evaluation"]["consensus"]["SA"],
                    "fc": p["jury_evaluation"]["consensus"]["FC"],
                })
            
            # grok at CL=0.0
            if "grok" in model and abs(cl - 0.0) < 0.01:
                resp = p["response"]
                has_meta = any(pat in resp for pat in ["Explanation:", "The query restricts", "**Explanation", "Note:"])
                report["grok"]["cl00_responses"].append({
                    "concept": concept,
                    "response": resp[:200],
                    "response_length": p["response_length"],
                    "has_meta_commentary": has_meta,
                    "cc": p["jury_evaluation"]["consensus"]["CC"],
                })

    # MiniMax ablation
    for r in ablation:
        if "MiniMax" not in r["subject_model"]:
            continue
        for p in r["performance"]:
            if abs(p["compression_level"] - 0.5) < 0.01:
                resp = p["response"]
                is_json_dump = "reasoningContent" in resp or resp.strip().startswith("[{")
                report["minimax"]["ablation_cl05"].append({
                    "concept": r["concept"],
                    "response_length": p["response_length"],
                    "is_json_dump": is_json_dump,
                    "cc": p["jury_evaluation"]["consensus"]["CC"],
                    "response_preview": resp[:100],
                })

    # Summary
    mm_base = report["minimax"]["baseline_cl05"]
    mm_abl = report["minimax"]["ablation_cl05"]
    grok_cl0 = report["grok"]["cl00_responses"]

    report["minimax"]["summary"] = {
        "domains_with_json_dump": sum(1 for x in mm_base if x["is_json_dump"]),
        "total_domains": len(mm_base),
        "mean_response_length": sum(x["response_length"] for x in mm_base) / len(mm_base) if mm_base else 0,
        "mean_cc_baseline": sum(x["cc"] for x in mm_base) / len(mm_base) if mm_base else 0,
        "ablation_json_dumps": sum(1 for x in mm_abl if x["is_json_dump"]),
        "mean_cc_ablation": sum(x["cc"] for x in mm_abl) / len(mm_abl) if mm_abl else 0,
        "mean_response_length_ablation": sum(x["response_length"] for x in mm_abl) / len(mm_abl) if mm_abl else 0,
    }

    meta_domains = [x["concept"] for x in grok_cl0 if x["has_meta_commentary"]]
    clean_domains = [x["concept"] for x in grok_cl0 if not x["has_meta_commentary"]]
    report["grok"]["summary"] = {
        "domains_with_meta": len(meta_domains),
        "domains_clean": len(clean_domains),
        "meta_domains": meta_domains,
        "clean_domains": clean_domains,
        "mean_cc_with_meta": sum(x["cc"] for x in grok_cl0 if x["has_meta_commentary"]) / max(len(meta_domains), 1),
        "mean_cc_clean": sum(x["cc"] for x in grok_cl0 if not x["has_meta_commentary"]) / max(len(clean_domains), 1),
    }

    with open("anomaly_report.json", "w") as f:
        json.dump(report, f, indent=2)

    # Print
    print("=== ANOMALY REPORT ===")
    print(f"\n--- MiniMax (Reasoning Trace Leakage) ---")
    print(f"JSON dumps at CL=0.5 (baseline): {report['minimax']['summary']['domains_with_json_dump']}/{report['minimax']['summary']['total_domains']}")
    print(f"Mean response length (baseline): {report['minimax']['summary']['mean_response_length']:.0f} words")
    print(f"Mean CC (baseline): {report['minimax']['summary']['mean_cc_baseline']:.3f}")
    print(f"JSON dumps at CL=0.5 (ablation): {report['minimax']['summary']['ablation_json_dumps']}/{len(mm_abl)}")
    print(f"Mean CC (ablation): {report['minimax']['summary']['mean_cc_ablation']:.3f}")
    print(f"Mean response length (ablation): {report['minimax']['summary']['mean_response_length_ablation']:.0f} words")

    print(f"\n--- grok-4-20-reasoning (Meta-Commentary) ---")
    print(f"Domains with meta-commentary at CL=0.0: {report['grok']['summary']['domains_with_meta']}/8")
    print(f"  Meta domains: {meta_domains}")
    print(f"  Clean domains: {clean_domains}")
    print(f"Mean CC (with meta): {report['grok']['summary']['mean_cc_with_meta']:.3f}")
    print(f"Mean CC (clean): {report['grok']['summary']['mean_cc_clean']:.3f}")
    print(f"\n✓ Saved to anomaly_report.json")

if __name__ == "__main__":
    main()
