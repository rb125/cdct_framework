import os
import sys
import glob
import subprocess
import threading
import json
from typing import List, Optional
from pathlib import Path
from mcp.server.fastmcp import FastMCP

# Add parent directory to path to ensure imports work
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from calculate_cdct_metrics import get_model_metrics
from models_config import SUBJECT_MODELS_CONFIG

# Initialize FastMCP server
mcp = FastMCP("CDCT Framework")

def run_diagnostic_battery_sync(model: str, concepts: Optional[List[str]] = None):
    """
    Runs main_jury.py for each concept for the given model.
    This is the internal implementation that can be run in a thread.
    """
    if concepts is None:
        concepts_dir = "concepts"
        concepts = glob.glob(os.path.join(concepts_dir, "*.json"))
    
    python_exe = sys.executable
    
    for concept_file in sorted(concepts):
        concept_name = os.path.splitext(os.path.basename(concept_file))[0]
        print(f"Running CDCT experiment: {concept_name} for model {model}")
        
        cmd = [
            python_exe, "main_jury.py",
            "--concept", concept_file,
            "--model", model
        ]
        
        try:
            # We run this synchronously here, but usually it's called in a thread
            subprocess.run(cmd, check=True)
            print(f"Completed experiment: {concept_name} for model {model}")
        except subprocess.CalledProcessError as e:
            print(f"Failed experiment: {concept_name} for model {model}. Error: {e}")

@mcp.tool()
def get_model_score(model_name: str) -> str:
    """
    Retrieve existing CDCT (Cross-Domain Compression Threshold) results for a specific model name.
    The CDCT metrics include SF, CRI, HOC, FAR', SAS', and CI.
    
    Args:
        model_name: The name of the model to retrieve scores for (e.g., 'gpt-5', 'DeepSeek-v3.1').
    """
    metrics = get_model_metrics(model_name)
    if not metrics:
        model_exists = any(config["model_name"].lower() == model_name.lower() for config in SUBJECT_MODELS_CONFIG)
        if model_exists:
            return f"No scores found for '{model_name}'. You can start a diagnostic battery using the 'run_experiment' tool."
        else:
            return f"Model '{model_name}' not found in configuration. Use 'list_available_models' to see supported models."
            
    return json.dumps(metrics, indent=2)

@mcp.tool()
def run_experiment(model_name: str, concepts: Optional[List[str]] = None) -> str:
    """
    Run a fresh CDCT diagnostic battery against a model. This is a long-running process
    that evaluates the model's performance across various semantic compression levels.
    
    Args:
        model_name: The name of the model to evaluate.
        concepts: Optional list of specific concept file paths to run. If None, all concepts in the 'concepts/' directory are used.
    """
    model_exists = any(config["model_name"].lower() == model_name.lower() for config in SUBJECT_MODELS_CONFIG)
    
    if not model_exists:
        return f"Model '{model_name}' not found. Use 'list_available_models' to see supported models."

    # Start in background thread to not block MCP tool response
    thread = threading.Thread(target=run_diagnostic_battery_sync, args=(model_name, concepts))
    thread.start()
    
    return f"Diagnostic battery started in background for model '{model_name}'. This may take several minutes to complete."

@mcp.tool()
def list_available_models() -> str:
    """
    List all models configured for CDCT evaluation and their architectural details.
    """
    models = []
    for config in SUBJECT_MODELS_CONFIG:
        models.append({
            "name": config["model_name"],
            "family": config.get("family", "Unknown"),
            "architecture": config.get("architecture", "Unknown"),
            "params": config.get("params", "Unknown")
        })
    return json.dumps(models, indent=2)

@mcp.tool()
def list_concepts() -> str:
    """
    List all available semantic concepts used in CDCT experiments.
    """
    concepts_dir = "concepts"
    concept_files = glob.glob(os.path.join(concepts_dir, "*.json"))
    concepts = [os.path.splitext(os.path.basename(f))[0] for f in concept_files]
    return json.dumps(sorted(concepts), indent=2)

if __name__ == "__main__":
    # Running via FastMCP default (stdio)
    mcp.run()
