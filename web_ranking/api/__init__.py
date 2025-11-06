"""
CDCT Model Ranking API
FastAPI-based REST API for ranking language models based on CDCT framework scores.
"""

from .main import app
from .data_processor import CDCTDataProcessor
from .models import *

__version__ = "1.0.0"
__all__ = ["app", "CDCTDataProcessor"]
