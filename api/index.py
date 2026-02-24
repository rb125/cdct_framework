import os
import sys

# Ensure the root directory is in sys.path
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root_dir)

# Import the original FastAPI app from cdct_api.py
from cdct_api import app

# This is the entry point Vercel will use for the REST API
