"""Compute all aggregate statistics needed for the TMLR paper."""
import json
import numpy as np
from pathlib import Path
from scipy import stats

RESULTS_DIR = Path("results_jury")
ABLATION_DIR = Path("results_jury_ablation")

def load_all(directory):
    results = []
    for f in sorted(directory.glob("*.json")):
        with open(f) as fh:
            results.append(json.load(fh))
    return results

def get_scores_at_cl(result, cl, dim):
    """Extract consensus score for dimension at compression level."""
    for p in result["performance"]:
        if abs(p["compression_level"] - cl) < 0.01:
            return p["jury_evaluation"]["consensus"].get(dim)
    return None

def main():
    baseline = load_all(RESULTS_DIR)
    ablation = load_all(ABLATION_DIR)
    print(f"Loaded {len(baseline)} baseline, {len(ablation)} ablation files")

    # --- Per-CL means (all models, excluding MiniMax) ---
    cls = [0.0, 0.25, 0.5, 0.75, 1.0]
    dims = ["CC", "SA", "FC"]
    
    all_scores = {d: {cl: [] for cl in cls} for d in dims}
    all_scores_no_minimax = {d: {cl: [] for cl in cls} for d in dims}
    
    # U-curve detection
    u_curve_all = 0
    u_curve_no_minimax = 0
    total_all = 0
    total_no_minimax = 0
    
    # For correlation
    cc_at_05_all = []
    sa_at_05_all = []
    cc_at_05_no_minimax = []
    sa_at_05_no_minimax = []
    
    # Agreement
    agreements = []
    cc_variances = []
    
    for r in baseline:
        model = r["subject_model"]
        is_minimax = "MiniMax" in model
        
        cc_0 = get_scores_at_cl(r, 0.0, "CC")
        cc_05 = get_scores_at_cl(r, 0.5, "CC")
        cc_1 = get_scores_at_cl(r, 1.0, "CC")
        sa_05 = get_scores_at_cl(r, 0.5, "SA")
        
        # Collect per-CL scores
        for cl in cls:
            for d in dims:
                v = get_scores_at_cl(r, cl, d)
                if v is not None:
                    all_scores[d][cl].append(v)
                    if not is_minimax:
                        all_scores_no_minimax[d][cl].append(v)
        
        # U-curve: CC at 0.5 < CC at 0.0 AND CC at 0.5 < CC at 1.0
        if cc_0 is not None and cc_05 is not None and cc_1 is not None:
            total_all += 1
            if cc_05 < cc_0 and cc_05 < cc_1:
                u_curve_all += 1
            if not is_minimax:
                total_no_minimax += 1
                if cc_05 < cc_0 and cc_05 < cc_1:
                    u_curve_no_minimax += 1
        
        # Correlation data
        if cc_05 is not None and sa_05 is not None:
            cc_at_05_all.append(cc_05)
            sa_at_05_all.append(sa_05)
            if not is_minimax:
                cc_at_05_no_minimax.append(cc_05)
                sa_at_05_no_minimax.append(sa_05)
        
        # Agreement metrics
        for p in r["performance"]:
            je = p.get("jury_evaluation", {}).get("consensus", {})
            if "agreement_score" in je:
                agreements.append(je["agreement_score"])
            if "judge_variance_CC" in je:
                cc_variances.append(je["judge_variance_CC"])

    # --- Ablation analysis ---
    ablation_deltas = []
    ablation_by_model = {}
    
    # Build baseline lookup: (model, concept) -> CC at CL=0.5
    baseline_lookup = {}
    for r in baseline:
        key = (r["subject_model"], r["concept"])
        cc_05 = get_scores_at_cl(r, 0.5, "CC")
        if cc_05 is not None:
            baseline_lookup[key] = cc_05
    
    for r in ablation:
        key = (r["subject_model"], r["concept"])
        abl_cc = get_scores_at_cl(r, 0.5, "CC")
        base_cc = baseline_lookup.get(key)
        if abl_cc is not None and base_cc is not None:
            delta = abl_cc - base_cc
            ablation_deltas.append(delta)
            model = r["subject_model"]
            if model not in ablation_by_model:
                ablation_by_model[model] = {"baseline": [], "ablated": [], "deltas": []}
            ablation_by_model[model]["baseline"].append(base_cc)
            ablation_by_model[model]["ablated"].append(abl_cc)
            ablation_by_model[model]["deltas"].append(delta)

    # --- Compute correlations ---
    r_all, p_all = stats.pearsonr(cc_at_05_all, sa_at_05_all)
    r_no_mm, p_no_mm = stats.pearsonr(cc_at_05_no_minimax, sa_at_05_no_minimax)

    # --- Compile report ---
    report = {
        "file_counts": {"baseline": len(baseline), "ablation": len(ablation)},
        "u_curve": {
            "all_models": {"count": u_curve_all, "total": total_all, "prevalence": u_curve_all / total_all if total_all else 0},
            "excluding_minimax": {"count": u_curve_no_minimax, "total": total_no_minimax, "prevalence": u_curve_no_minimax / total_no_minimax if total_no_minimax else 0},
        },
        "mean_scores_by_cl": {
            d: {str(cl): {"mean": float(np.mean(all_scores_no_minimax[d][cl])), "std": float(np.std(all_scores_no_minimax[d][cl])), "n": len(all_scores_no_minimax[d][cl])}
                for cl in cls}
            for d in dims
        },
        "correlation_cc_sa_at_05": {
            "all_models": {"r": float(r_all), "p": float(p_all), "n": len(cc_at_05_all)},
            "excluding_minimax": {"r": float(r_no_mm), "p": float(p_no_mm), "n": len(cc_at_05_no_minimax)},
        },
        "ablation": {
            "mean_delta": float(np.mean(ablation_deltas)),
            "median_delta": float(np.median(ablation_deltas)),
            "positive_count": sum(1 for d in ablation_deltas if d > 0),
            "total": len(ablation_deltas),
            "by_model": {m: {"mean_baseline": float(np.mean(v["baseline"])), "mean_ablated": float(np.mean(v["ablated"])), "mean_delta": float(np.mean(v["deltas"]))}
                         for m, v in sorted(ablation_by_model.items())},
        },
        "jury_agreement": {
            "mean_agreement": float(np.mean(agreements)),
            "std_agreement": float(np.std(agreements)),
            "mean_cc_variance": float(np.mean(cc_variances)),
        },
        "differential_sensitivity": {
            "cc_drop_at_05": float(np.mean(all_scores_no_minimax["CC"][1.0]) - np.mean(all_scores_no_minimax["CC"][0.5])),
            "sa_drop_at_05": float(np.mean(all_scores_no_minimax["SA"][1.0]) - np.mean(all_scores_no_minimax["SA"][0.5])),
        },
    }
    
    # Compute ratio
    cc_drop = report["differential_sensitivity"]["cc_drop_at_05"]
    sa_drop = report["differential_sensitivity"]["sa_drop_at_05"]
    report["differential_sensitivity"]["ratio"] = cc_drop / sa_drop if sa_drop != 0 else float("inf")

    with open("paper_statistics.json", "w") as f:
        json.dump(report, f, indent=2)

    # Print summary
    print("\n=== PAPER STATISTICS SUMMARY ===")
    print(f"\nU-curve prevalence (all): {report['u_curve']['all_models']['count']}/{report['u_curve']['all_models']['total']} = {report['u_curve']['all_models']['prevalence']:.1%}")
    print(f"U-curve prevalence (excl MiniMax): {report['u_curve']['excluding_minimax']['count']}/{report['u_curve']['excluding_minimax']['total']} = {report['u_curve']['excluding_minimax']['prevalence']:.1%}")
    print(f"\nCC-SA correlation at CL=0.5 (all): r={r_all:.3f}, p={p_all:.4f}")
    print(f"CC-SA correlation at CL=0.5 (excl MiniMax): r={r_no_mm:.3f}, p={p_no_mm:.4f}")
    print(f"\nMean scores at CL=0.5 (excl MiniMax):")
    for d in dims:
        print(f"  {d}: {report['mean_scores_by_cl'][d]['0.5']['mean']:.3f} ± {report['mean_scores_by_cl'][d]['0.5']['std']:.3f}")
    print(f"\nMean scores at CL=0.0 (excl MiniMax):")
    for d in dims:
        print(f"  {d}: {report['mean_scores_by_cl'][d]['0.0']['mean']:.3f} ± {report['mean_scores_by_cl'][d]['0.0']['std']:.3f}")
    print(f"\nMean scores at CL=1.0 (excl MiniMax):")
    for d in dims:
        print(f"  {d}: {report['mean_scores_by_cl'][d]['1.0']['mean']:.3f} ± {report['mean_scores_by_cl'][d]['1.0']['std']:.3f}")
    print(f"\nDifferential sensitivity: CC drop={cc_drop:.3f}, SA drop={sa_drop:.3f}, ratio={report['differential_sensitivity']['ratio']:.1f}x")
    print(f"\nAblation: mean delta={report['ablation']['mean_delta']:.3f}, positive={report['ablation']['positive_count']}/{report['ablation']['total']}")
    print(f"Jury agreement: mean={report['jury_agreement']['mean_agreement']:.3f}, CC variance={report['jury_agreement']['mean_cc_variance']:.3f}")
    print(f"\nAblation by model:")
    for m, v in sorted(report["ablation"]["by_model"].items()):
        print(f"  {m}: baseline={v['mean_baseline']:.3f} → ablated={v['mean_ablated']:.3f} (Δ={v['mean_delta']:.3f})")
    print(f"\n✓ Saved to paper_statistics.json")

if __name__ == "__main__":
    main()
