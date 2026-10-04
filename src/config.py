import os
from pathlib import Path

# Project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Input/output files
PREDICTION_FILE = PROJECT_ROOT / "results" / "predictions.csv"
ALLOCATION_FILE = PROJECT_ROOT / "results" / "resource_allocation.csv"

# Cluster capacity
TOTAL_CPU = float(os.getenv("CLUSTER_CPU", "1.0"))
TOTAL_MEMORY = float(os.getenv("CLUSTER_MEMORY", "1.0"))