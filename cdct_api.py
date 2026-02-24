from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional
import os
import glob
import subprocess
import sys
import json
from pathlib import Path
from calculate_cdct_metrics import get_model_metrics

app = FastAPI(title="CDCT API")

class ExperimentRequest(BaseModel):
    model: str
    concepts: Optional[List[str]] = None

@app.get("/score/{model_name}")
async def get_score(model_name: str, background_tasks: BackgroundTasks):
    """
    Retrieve existing CDCT results for a specific model name.
    If no results exist, trigger a fresh diagnostic battery in the background.
    """
    metrics = get_model_metrics(model_name)
    if not metrics:
        # Verify model exists in config before starting experiment
        from models_config import SUBJECT_MODELS_CONFIG
        model_exists = any(config["model_name"].lower() == model_name.lower() for config in SUBJECT_MODELS_CONFIG)
        
        if model_exists:
            if os.getenv("VERCEL") or os.getenv("VERCEL_ENV"):
                return {
                    "status": "error",
                    "message": (
                        f"No scores found for '{model_name}'. Background scoring is disabled on Vercel. "
                        "Commit results to results_jury/ or run scoring on a worker."
                    ),
                }
            background_tasks.add_task(run_diagnostic_battery, model_name)
            return {"status": "started", "message": f"No scores found for '{model_name}'. Diagnostic battery started in background."}
        else:
            raise HTTPException(status_code=404, detail=f"Model '{model_name}' not found in SUBJECT_MODELS_CONFIG")
            
    return metrics

def run_diagnostic_battery(model: str, concepts: Optional[List[str]] = None):
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
            # Running synchronously for now, but in a background task
            subprocess.run(cmd, check=True)
            print(f"Completed experiment: {concept_name} for model {model}")
        except subprocess.CalledProcessError as e:
            print(f"Failed experiment: {concept_name} for model {model}. Error: {e}")

@app.post("/run_experiment")
async def run_experiment(request: ExperimentRequest, background_tasks: BackgroundTasks):
    """
    Run a fresh diagnostic battery against a model.
    """
    # Verify model exists in config
    from models_config import SUBJECT_MODELS_CONFIG
    model_exists = any(config["model_name"].lower() == request.model.lower() for config in SUBJECT_MODELS_CONFIG)
    
    if not model_exists:
        raise HTTPException(status_code=400, detail=f"Model '{request.model}' not found in SUBJECT_MODELS_CONFIG")

    if os.getenv("VERCEL") or os.getenv("VERCEL_ENV"):
        return {
            "status": "error",
            "model": request.model,
            "message": "Background scoring is disabled on Vercel. Run on a worker or locally, then commit results.",
        }

    background_tasks.add_task(run_diagnostic_battery, request.model, request.concepts)
    return {"status": "started", "model": request.model, "message": "Diagnostic battery started in background."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
