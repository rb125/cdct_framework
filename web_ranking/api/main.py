"""
FastAPI application for CDCT Model Ranking.
Provides REST API for model rankings, comparisons, and analysis.
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from typing import List, Optional
from pathlib import Path

from .data_processor import CDCTDataProcessor
from .models import (
    RankingsResponse,
    ModelRanking,
    DomainRanking,
    ModelDetails,
    ModelComparison,
    PerformanceData,
    DomainsResponse,
    ModelsResponse,
    HealthResponse
)

# Initialize FastAPI app
app = FastAPI(
    title="CDCT Model Ranking API",
    description="API for ranking language models based on CDCT framework scores",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize data processor
data_processor = CDCTDataProcessor()

# Mount static files
static_dir = Path(__file__).parent.parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


@app.on_event("startup")
async def startup_event():
    """Load data on startup."""
    try:
        data_processor.load_consolidated_results()
        print("✓ Consolidated results loaded successfully")
    except Exception as e:
        print(f"⚠ Warning: Could not load consolidated results: {e}")


@app.get("/", response_class=FileResponse)
async def serve_frontend():
    """Serve the frontend application."""
    index_file = static_dir / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return {"message": "CDCT Model Ranking API", "docs": "/api/docs"}


@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "message": "CDCT Model Ranking API is running",
        "version": "1.0.0"
    }


@app.get("/api/rankings", response_model=RankingsResponse)
async def get_rankings(
    sort_by: str = Query("CSI", description="Metric to sort by (CSI, C_h, mean_score)"),
    ascending: bool = Query(True, description="Sort ascending (True) or descending (False)")
):
    """
    Get overall model rankings.

    Args:
        sort_by: Metric to sort by (CSI, C_h, mean_score)
        ascending: Sort order (True = ascending, False = descending)

    Returns:
        Model rankings with aggregated statistics
    """
    try:
        rankings = data_processor.get_overall_rankings(sort_by=sort_by, ascending=ascending)
        return {
            "total": len(rankings),
            "rankings": rankings
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching rankings: {str(e)}")


@app.get("/api/domains", response_model=DomainsResponse)
async def get_domains():
    """
    Get list of all available domains.

    Returns:
        List of domain names
    """
    try:
        domains = data_processor.get_all_domains()
        return {
            "total": len(domains),
            "domains": sorted(domains)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching domains: {str(e)}")


@app.get("/api/domains/{domain}/rankings", response_model=List[DomainRanking])
async def get_domain_rankings(domain: str):
    """
    Get model rankings for a specific domain.

    Args:
        domain: Domain name (e.g., 'mathematics', 'physics')

    Returns:
        Model rankings for the specified domain
    """
    try:
        rankings = data_processor.get_domain_rankings(domain)
        if not rankings:
            raise HTTPException(status_code=404, detail=f"Domain '{domain}' not found")
        return rankings
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching domain rankings: {str(e)}")


@app.get("/api/models", response_model=ModelsResponse)
async def get_models():
    """
    Get list of all tested models.

    Returns:
        List of model names
    """
    try:
        models = data_processor.get_all_models()
        return {
            "total": len(models),
            "models": sorted(models)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching models: {str(e)}")


@app.get("/api/models/{model_name}", response_model=ModelDetails)
async def get_model_details(model_name: str):
    """
    Get detailed statistics for a specific model.

    Args:
        model_name: Name of the model

    Returns:
        Detailed model statistics across all experiments
    """
    try:
        details = data_processor.get_model_details(model_name)
        if not details:
            raise HTTPException(status_code=404, detail=f"Model '{model_name}' not found")
        return details
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching model details: {str(e)}")


@app.get("/api/compare", response_model=ModelComparison)
async def compare_models(
    models: List[str] = Query(..., description="Model names to compare (comma-separated)")
):
    """
    Compare multiple models side-by-side.

    Args:
        models: List of model names to compare

    Returns:
        Comparison data for the specified models
    """
    try:
        if len(models) < 2:
            raise HTTPException(status_code=400, detail="At least 2 models required for comparison")

        comparison = data_processor.compare_models(models)
        if not comparison["stats"]:
            raise HTTPException(status_code=404, detail="No data found for specified models")

        return comparison
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error comparing models: {str(e)}")


@app.get("/api/performance/{model_name}/{concept}", response_model=PerformanceData)
async def get_performance_data(model_name: str, concept: str):
    """
    Get detailed performance data for a specific model-concept combination.

    Args:
        model_name: Name of the model
        concept: Concept name

    Returns:
        Performance data across compression levels
    """
    try:
        data = data_processor.get_performance_data(model_name, concept)
        if not data:
            raise HTTPException(
                status_code=404,
                detail=f"No performance data found for model '{model_name}' and concept '{concept}'"
            )
        return data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching performance data: {str(e)}")


@app.get("/api/stats/summary")
async def get_summary_stats():
    """
    Get summary statistics across all models and domains.

    Returns:
        Overall summary statistics
    """
    try:
        rankings = data_processor.get_overall_rankings()
        domains = data_processor.get_all_domains()

        if not rankings:
            return {
                "total_models": 0,
                "total_domains": 0,
                "total_experiments": 0,
                "best_model": None,
                "metrics_overview": {}
            }

        # Find best model for each metric
        best_csi = min(rankings, key=lambda x: x["CSI"]["mean"])
        best_ch = min((r for r in rankings if r["C_h"]["mean"] is not None), key=lambda x: x["C_h"]["mean"], default=None)
        best_score = max((r for r in rankings if r["mean_score"]["mean"] is not None), key=lambda x: x["mean_score"]["mean"], default=None)

        total_experiments = sum(r["n_experiments"] for r in rankings)

        return {
            "total_models": len(rankings),
            "total_domains": len(domains),
            "total_experiments": total_experiments,
            "best_models": {
                "CSI": {
                    "model": best_csi["model"],
                    "value": best_csi["CSI"]["mean"]
                },
                "C_h": {
                    "model": best_ch["model"] if best_ch else None,
                    "value": best_ch["C_h"]["mean"] if best_ch else None
                },
                "mean_score": {
                    "model": best_score["model"] if best_score else None,
                    "value": best_score["mean_score"]["mean"] if best_score else None
                }
            },
            "metrics_overview": {
                "CSI": {
                    "best": min(r["CSI"]["mean"] for r in rankings),
                    "worst": max(r["CSI"]["mean"] for r in rankings),
                    "average": sum(r["CSI"]["mean"] for r in rankings) / len(rankings)
                },
                "domains": domains
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching summary stats: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
