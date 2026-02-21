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
            subprocess.run(cmd, check=True)
            print(f"Completed experiment: {concept_name} for model {model}")
        except subprocess.CalledProcessError as e:
            print(f"Failed experiment: {concept_name} for model {model}. Error: {e}")

@mcp.tool()
def get_model_score(model: str) -> str:
    """
    Retrieve existing CDCT results for a specific model name.
    
    Args:
        model: The name of the model to retrieve scores for.
    """
    metrics = get_model_metrics(model)
    if not metrics:
        model_exists = any(config["model_name"].lower() == model.lower() for config in SUBJECT_MODELS_CONFIG)
        if model_exists:
            return f"No scores found for '{model}'. You can start a diagnostic battery using the 'run_experiment' tool."
        else:
            return f"Model '{model}' not found in configuration."
            
    return json.dumps(metrics, indent=2)

@mcp.tool()
def run_experiment(model: str, concepts: Optional[List[str]] = None) -> str:
    """
    Run a fresh CDCT diagnostic battery against a model.
    """
    model_exists = any(config["model_name"].lower() == model.lower() for config in SUBJECT_MODELS_CONFIG)
    
    if not model_exists:
        return f"Model '{model}' not found."

    thread = threading.Thread(target=run_diagnostic_battery_sync, args=(model, concepts))
    thread.start()
    
    return f"Diagnostic battery started in background for model '{model}'."

@mcp.tool()
def list_available_models() -> str:
    """
    List all models configured for CDCT evaluation.
    """
    models = []
    for config in SUBJECT_MODELS_CONFIG:
        models.append({
            "name": config["model_name"],
            "family": config.get("family", "Unknown"),
            "architecture": config.get("architecture", "Unknown")
        })
    return json.dumps(models, indent=2)

@mcp.tool()
def list_concepts() -> str:
    """
    List all available semantic concepts.
    """
    concepts_dir = "concepts"
    concept_files = glob.glob(os.path.join(concepts_dir, "*.json"))
    concepts = [os.path.splitext(os.path.basename(f))[0] for f in concept_files]
    return json.dumps(sorted(concepts), indent=2)

@mcp.tool()
def server_status() -> str:
    """
    Check the health and environment of the CDCT MCP server.
    """
    is_vercel = "VERCEL" in os.environ
    return json.dumps({
        "status": "online",
        "environment": "Vercel" if is_vercel else "Local/Other",
        "writable_filesystem": not is_vercel,
        "features": {
            "score_retrieval": "active",
            "experiment_execution": "local_only" if is_vercel else "active"
        }
    })

if __name__ == "__main__":
    # If run directly, default to stdio (CLI usage)
    mcp.run()
