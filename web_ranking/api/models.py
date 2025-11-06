"""
Pydantic models for the CDCT Model Ranking API.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class MetricStats(BaseModel):
    """Statistical metrics for a model's performance."""
    mean: Optional[float] = Field(None, description="Mean value")
    std: Optional[float] = Field(None, description="Standard deviation")
    min: Optional[float] = Field(None, description="Minimum value")
    max: Optional[float] = Field(None, description="Maximum value")


class ModelRanking(BaseModel):
    """Model ranking information."""
    rank: int = Field(..., description="Rank position (1 = best)")
    model: str = Field(..., description="Model name")
    n_experiments: int = Field(..., description="Number of experiments")
    CSI: MetricStats = Field(..., description="Compression Stability Index stats")
    C_h: MetricStats = Field(..., description="Comprehension Horizon stats")
    mean_score: MetricStats = Field(..., description="Mean performance score stats")
    R_squared: MetricStats = Field(..., description="R-squared stats")
    concepts: List[str] = Field(default_factory=list, description="Tested concepts")


class DomainRanking(BaseModel):
    """Model ranking for a specific domain."""
    rank: int = Field(..., description="Rank position in domain")
    model: str = Field(..., description="Model name")
    domain: str = Field(..., description="Domain name")
    concept: Optional[str] = Field(None, description="Concept name")
    CSI: Optional[float] = Field(None, description="Compression Stability Index")
    C_h: Optional[float] = Field(None, description="Comprehension Horizon")
    mean_score: Optional[float] = Field(None, description="Mean performance score")
    R_squared: Optional[float] = Field(None, description="R-squared value")
    decay_direction: Optional[str] = Field(None, description="Decay direction")
    n_compression_levels: Optional[int] = Field(None, description="Number of compression levels")


class ConceptPerformance(BaseModel):
    """Performance data for a concept."""
    concept: str = Field(..., description="Concept name")
    CSI: Optional[float] = Field(None, description="Compression Stability Index")
    C_h: Optional[float] = Field(None, description="Comprehension Horizon")
    mean_score: Optional[float] = Field(None, description="Mean performance score")
    R_squared: Optional[float] = Field(None, description="R-squared value")
    decay_direction: Optional[str] = Field(None, description="Decay direction")
    strategy: Optional[str] = Field(None, description="Prompting strategy")
    evaluation_mode: Optional[str] = Field(None, description="Evaluation mode")


class ModelDetails(BaseModel):
    """Detailed model statistics."""
    model: str = Field(..., description="Model name")
    total_experiments: int = Field(..., description="Total number of experiments")
    overall_stats: Dict[str, MetricStats] = Field(..., description="Overall statistics")
    by_domain: Dict[str, List[ConceptPerformance]] = Field(..., description="Performance by domain")


class ModelComparison(BaseModel):
    """Comparison data for multiple models."""
    models: List[str] = Field(..., description="Models being compared")
    stats: List[Dict[str, Any]] = Field(..., description="Comparison statistics")


class PerformanceLevel(BaseModel):
    """Performance at a single compression level."""
    compression_level: int = Field(..., description="Compression level index")
    context_length: int = Field(..., description="Context length in words")
    response_length: int = Field(..., description="Response length in words")
    score: float = Field(..., description="Performance score (0-1)")
    verdict: str = Field(..., description="Qualitative verdict")
    hallucinated: List[str] = Field(default_factory=list, description="Hallucinated words")
    response: str = Field(..., description="Model response")


class PerformanceData(BaseModel):
    """Detailed performance data for a model-concept combination."""
    model: str = Field(..., description="Model name")
    concept: str = Field(..., description="Concept name")
    performance: List[Dict[str, Any]] = Field(..., description="Performance across compression levels")
    analysis: Dict[str, Any] = Field(..., description="Analysis metrics")
    metadata: Dict[str, Any] = Field(..., description="Experiment metadata")


class RankingsResponse(BaseModel):
    """Response model for rankings endpoint."""
    total: int = Field(..., description="Total number of models")
    rankings: List[ModelRanking] = Field(..., description="Model rankings")


class DomainsResponse(BaseModel):
    """Response model for domains list."""
    total: int = Field(..., description="Total number of domains")
    domains: List[str] = Field(..., description="Available domains")


class ModelsResponse(BaseModel):
    """Response model for models list."""
    total: int = Field(..., description="Total number of models")
    models: List[str] = Field(..., description="Available models")


class HealthResponse(BaseModel):
    """Health check response."""
    status: str = Field(..., description="Service status")
    message: str = Field(..., description="Status message")
    version: str = Field(default="1.0.0", description="API version")
