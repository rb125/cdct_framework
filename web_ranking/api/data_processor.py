"""
Data processor for CDCT framework results.
Loads and processes experimental results for the ranking API.
"""

import json
import os
import math
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from statistics import mean, stdev


class CDCTDataProcessor:
    """Process CDCT experimental results for ranking and analysis."""

    def __init__(self, results_dir: str = None, consolidated_file: str = None):
        """
        Initialize the data processor.

        Args:
            results_dir: Path to results directory (default: ../../results)
            consolidated_file: Path to consolidated results JSON (default: ../../consolidated_results.json)
        """
        self.base_dir = Path(__file__).parent.parent.parent
        self.results_dir = Path(results_dir) if results_dir else self.base_dir / "results"
        self.consolidated_file = Path(consolidated_file) if consolidated_file else self.base_dir / "consolidated_results.json"

        self._consolidated_data = None
        self._individual_results = None

    def load_consolidated_results(self) -> Dict:
        """Load consolidated results JSON file."""
        if not self.consolidated_file.exists():
            raise FileNotFoundError(f"Consolidated results not found: {self.consolidated_file}")

        with open(self.consolidated_file, 'r') as f:
            self._consolidated_data = json.load(f)

        return self._consolidated_data

    def load_individual_results(self) -> Dict[str, Dict]:
        """Load all individual result files from results directory."""
        if not self.results_dir.exists():
            raise FileNotFoundError(f"Results directory not found: {self.results_dir}")

        results = {}
        for result_file in self.results_dir.glob("results_*.json"):
            with open(result_file, 'r') as f:
                data = json.load(f)
                results[result_file.stem] = data

        self._individual_results = results
        return results

    def get_overall_rankings(self, sort_by: str = "CSI", ascending: bool = True) -> List[Dict]:
        """
        Get overall model rankings.

        Args:
            sort_by: Metric to sort by (CSI, C_h, mean_score)
            ascending: Sort ascending (True) or descending (False)

        Returns:
            List of model rankings with aggregated stats
        """
        if self._consolidated_data is None:
            self.load_consolidated_results()

        rankings = []
        by_model = self._consolidated_data.get("by_model", {})

        for model_name, experiments in by_model.items():
            if not experiments:
                continue

            # Extract metrics from all experiments for this model (filter out None and NaN)
            csi_values = [exp.get("analysis", {}).get("CSI") for exp in experiments
                         if exp.get("analysis", {}).get("CSI") is not None and not math.isnan(exp.get("analysis", {}).get("CSI", float('nan')))]
            ch_values = [exp.get("analysis", {}).get("C_h") for exp in experiments
                        if exp.get("analysis", {}).get("C_h") is not None and not math.isnan(exp.get("analysis", {}).get("C_h", float('nan')))]
            mean_scores = [exp.get("analysis", {}).get("mean_score") for exp in experiments
                          if exp.get("analysis", {}).get("mean_score") is not None and not math.isnan(exp.get("analysis", {}).get("mean_score", float('nan')))]
            r_squared_values = [exp.get("analysis", {}).get("R_squared") for exp in experiments
                               if exp.get("analysis", {}).get("R_squared") is not None and not math.isnan(exp.get("analysis", {}).get("R_squared", float('nan')))]

            if not csi_values:
                continue

            model_stats = {
                "model": model_name,
                "n_experiments": len(experiments),
                "CSI": {
                    "mean": mean(csi_values),
                    "std": stdev(csi_values) if len(csi_values) > 1 else 0.0,
                    "min": min(csi_values),
                    "max": max(csi_values)
                },
                "C_h": {
                    "mean": mean(ch_values) if ch_values else None,
                    "std": stdev(ch_values) if len(ch_values) > 1 else 0.0,
                    "min": min(ch_values) if ch_values else None,
                    "max": max(ch_values) if ch_values else None
                },
                "mean_score": {
                    "mean": mean(mean_scores) if mean_scores else None,
                    "std": stdev(mean_scores) if len(mean_scores) > 1 else 0.0,
                    "min": min(mean_scores) if mean_scores else None,
                    "max": max(mean_scores) if mean_scores else None
                },
                "R_squared": {
                    "mean": mean(r_squared_values) if r_squared_values else None,
                    "std": stdev(r_squared_values) if len(r_squared_values) > 1 else (0.0 if r_squared_values else None)
                },
                "concepts": list(set(exp.get("metadata", {}).get("concept") for exp in experiments if exp.get("metadata", {}).get("concept")))
            }

            rankings.append(model_stats)

        # Sort by specified metric
        sort_key_map = {
            "CSI": lambda x: x["CSI"]["mean"],
            "C_h": lambda x: x["C_h"]["mean"] if x["C_h"]["mean"] is not None else float('inf'),
            "mean_score": lambda x: x["mean_score"]["mean"] if x["mean_score"]["mean"] is not None else 0
        }

        if sort_by in sort_key_map:
            rankings.sort(key=sort_key_map[sort_by], reverse=not ascending)

        # Add rank
        for idx, ranking in enumerate(rankings, 1):
            ranking["rank"] = idx

        return rankings

    def get_domain_rankings(self, domain: str) -> List[Dict]:
        """
        Get model rankings for a specific domain.

        Args:
            domain: Domain name (e.g., 'mathematics', 'physics')

        Returns:
            List of model rankings for the specified domain
        """
        if self._consolidated_data is None:
            self.load_consolidated_results()

        by_domain = self._consolidated_data.get("by_domain", {})

        if domain not in by_domain:
            return []

        experiments = by_domain[domain]
        model_stats = {}

        for exp in experiments:
            # Try both direct field and metadata field for compatibility
            model_name = exp.get("model") or exp.get("metadata", {}).get("model")
            if not model_name:
                continue

            analysis = exp.get("analysis", {})
            concept = exp.get("concept") or exp.get("metadata", {}).get("concept")

            if model_name not in model_stats:
                model_stats[model_name] = {
                    "model": model_name,
                    "domain": domain,
                    "concept": concept,
                    "CSI": analysis.get("CSI"),
                    "C_h": analysis.get("C_h"),
                    "mean_score": analysis.get("mean_score"),
                    "R_squared": analysis.get("R_squared"),
                    "decay_direction": analysis.get("decay_direction"),
                    "n_compression_levels": analysis.get("n_compression_levels")
                }

        rankings = list(model_stats.values())
        rankings.sort(key=lambda x: x["CSI"] if x["CSI"] is not None else float('inf'))

        for idx, ranking in enumerate(rankings, 1):
            ranking["rank"] = idx

        return rankings

    def get_all_domains(self) -> List[str]:
        """Get list of all available domains."""
        if self._consolidated_data is None:
            self.load_consolidated_results()

        return list(self._consolidated_data.get("by_domain", {}).keys())

    def get_all_models(self) -> List[str]:
        """Get list of all tested models."""
        if self._consolidated_data is None:
            self.load_consolidated_results()

        return list(self._consolidated_data.get("by_model", {}).keys())

    def get_model_details(self, model_name: str) -> Dict:
        """
        Get detailed statistics for a specific model.

        Args:
            model_name: Name of the model

        Returns:
            Detailed model statistics across all experiments
        """
        if self._consolidated_data is None:
            self.load_consolidated_results()

        by_model = self._consolidated_data.get("by_model", {})

        if model_name not in by_model:
            return None

        experiments = by_model[model_name]

        # Group experiments by domain
        by_domain = {}
        for exp in experiments:
            metadata = exp.get("metadata", {})
            domain = self._extract_domain(metadata.get("concept", ""))

            if domain not in by_domain:
                by_domain[domain] = []

            by_domain[domain].append({
                "concept": metadata.get("concept"),
                "CSI": exp.get("analysis", {}).get("CSI"),
                "C_h": exp.get("analysis", {}).get("C_h"),
                "mean_score": exp.get("analysis", {}).get("mean_score"),
                "R_squared": exp.get("analysis", {}).get("R_squared"),
                "decay_direction": exp.get("analysis", {}).get("decay_direction"),
                "strategy": metadata.get("strategy"),
                "evaluation_mode": metadata.get("evaluation_mode")
            })

        # Calculate overall statistics
        all_csi = [exp.get("analysis", {}).get("CSI") for exp in experiments if exp.get("analysis", {}).get("CSI") is not None]
        all_ch = [exp.get("analysis", {}).get("C_h") for exp in experiments if exp.get("analysis", {}).get("C_h") is not None]
        all_scores = [exp.get("analysis", {}).get("mean_score") for exp in experiments if exp.get("analysis", {}).get("mean_score") is not None]

        return {
            "model": model_name,
            "total_experiments": len(experiments),
            "overall_stats": {
                "CSI": {
                    "mean": mean(all_csi) if all_csi else None,
                    "std": stdev(all_csi) if len(all_csi) > 1 else 0.0,
                    "min": min(all_csi) if all_csi else None,
                    "max": max(all_csi) if all_csi else None
                },
                "C_h": {
                    "mean": mean(all_ch) if all_ch else None,
                    "std": stdev(all_ch) if len(all_ch) > 1 else 0.0,
                    "min": min(all_ch) if all_ch else None,
                    "max": max(all_ch) if all_ch else None
                },
                "mean_score": {
                    "mean": mean(all_scores) if all_scores else None,
                    "std": stdev(all_scores) if len(all_scores) > 1 else 0.0,
                    "min": min(all_scores) if all_scores else None,
                    "max": max(all_scores) if all_scores else None
                }
            },
            "by_domain": by_domain,
            "experiments": experiments
        }

    def compare_models(self, model_names: List[str]) -> Dict:
        """
        Compare multiple models side-by-side.

        Args:
            model_names: List of model names to compare

        Returns:
            Comparison data for the specified models
        """
        comparison = {
            "models": model_names,
            "stats": []
        }

        for model_name in model_names:
            details = self.get_model_details(model_name)
            if details:
                comparison["stats"].append({
                    "model": model_name,
                    "overall": details["overall_stats"],
                    "n_experiments": details["total_experiments"]
                })

        return comparison

    def _extract_domain(self, concept: str) -> str:
        """Extract domain from concept name (e.g., 'derivative' -> 'mathematics')."""
        domain_mapping = {
            "derivative": "mathematics",
            "f_equals_ma": "physics",
            "natural_selection": "biology",
            "recursion": "computer_science",
            "impressionism": "art",
            "harm_principle": "ethics",
            "modus_ponens": "logic",
            "phoneme": "linguistics"
        }

        return domain_mapping.get(concept, "unknown")

    def get_performance_data(self, model_name: str, concept: str) -> Optional[Dict]:
        """
        Get detailed performance data for a specific model-concept combination.

        Args:
            model_name: Name of the model
            concept: Concept name

        Returns:
            Performance data across compression levels
        """
        if self._consolidated_data is None:
            self.load_consolidated_results()

        by_model = self._consolidated_data.get("by_model", {})

        if model_name not in by_model:
            return None

        for exp in by_model[model_name]:
            if exp.get("metadata", {}).get("concept") == concept:
                return {
                    "model": model_name,
                    "concept": concept,
                    "performance": exp.get("performance", []),
                    "analysis": exp.get("analysis", {}),
                    "metadata": exp.get("metadata", {})
                }

        return None
