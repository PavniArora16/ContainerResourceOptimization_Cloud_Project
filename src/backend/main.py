from pathlib import Path
import subprocess
import sys

import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

RESULTS_DIR = PROJECT_ROOT / "results"

PREDICTIONS_FILE = RESULTS_DIR / "predictions.csv"
ALLOCATIONS_FILE = RESULTS_DIR / "resource_allocation.csv"


# ============================================================
# FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title="Container Resource Optimization API",
    description=(
        "Backend API for ML-based container workload prediction "
        "and intelligent resource allocation."
    ),
    version="1.0.0"
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def load_csv(file_path: Path) -> pd.DataFrame:
    """
    Load a CSV file and return it as a pandas DataFrame.
    """

    if not file_path.exists():
        raise FileNotFoundError(
            f"Required file not found: {file_path}"
        )

    return pd.read_csv(file_path)


def dataframe_to_records(df: pd.DataFrame):
    """
    Convert DataFrame into JSON-compatible records.
    """

    return df.where(pd.notnull(df), None).to_dict(
        orient="records"
    )


# ============================================================
# ROOT ENDPOINT
# ============================================================

@app.get("/")
def root():
    return {
        "message": "Container Resource Optimization API",
        "status": "running",
        "version": "1.0.0"
    }


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/health")
def health_check():

    return {
        "status": "healthy",
        "service": "container-resource-optimization-backend"
    }


# ============================================================
# PREDICTIONS
# ============================================================

@app.get("/predictions")
def get_predictions():

    try:
        df = load_csv(PREDICTIONS_FILE)

        return {
            "count": len(df),
            "predictions": dataframe_to_records(df)
        }

    except FileNotFoundError as e:

        raise HTTPException(
            status_code=404,
            detail=str(e)
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Could not load predictions: {str(e)}"
        )


# ============================================================
# RESOURCE ALLOCATIONS
# ============================================================

@app.get("/allocations")
def get_allocations():

    try:
        df = load_csv(ALLOCATIONS_FILE)

        return {
            "count": len(df),
            "allocations": dataframe_to_records(df)
        }

    except FileNotFoundError as e:

        raise HTTPException(
            status_code=404,
            detail=str(e)
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Could not load allocations: {str(e)}"
        )


# ============================================================
# METRICS
# ============================================================

@app.get("/metrics")
def get_metrics():

    try:

        predictions = load_csv(PREDICTIONS_FILE)
        allocations = load_csv(ALLOCATIONS_FILE)

        # ----------------------------------------------------
        # Prediction metrics
        # ----------------------------------------------------

        total_tasks = len(predictions)

        # ----------------------------------------------------
        # Allocation metrics
        # ----------------------------------------------------

        total_cpu_allocated = float(
            allocations["allocated_cpu"].sum()
        )

        total_memory_allocated = float(
            allocations["allocated_memory"].sum()
        )

        total_cpu_available = 1.0
        total_memory_available = 1.0

        cpu_utilization = (
            total_cpu_allocated / total_cpu_available
        ) * 100

        memory_utilization = (
            total_memory_allocated / total_memory_available
        ) * 100

        # ----------------------------------------------------
        # Allocation status
        # ----------------------------------------------------

        status_counts = (
            allocations["allocation_status"]
            .value_counts()
            .to_dict()
        )

        full_allocations = int(
            status_counts.get("FULL", 0)
        )

        partial_allocations = int(
            status_counts.get("PARTIAL", 0)
        )

        unmet_allocations = int(
            status_counts.get("UNMET", 0)
        )

        # ----------------------------------------------------
        # Priority distribution
        # ----------------------------------------------------

        priority_counts = (
            allocations["priority"]
            .value_counts()
            .sort_index()
            .to_dict()
        )

        # Convert possible numpy integer keys
        priority_counts = {
            str(k): int(v)
            for k, v in priority_counts.items()
        }

        return {
            "total_tasks": total_tasks,

            "cpu": {
                "available": total_cpu_available,
                "allocated": round(
                    total_cpu_allocated, 4
                ),
                "utilization_percent": round(
                    cpu_utilization, 2
                )
            },

            "memory": {
                "available": total_memory_available,
                "allocated": round(
                    total_memory_allocated, 4
                ),
                "utilization_percent": round(
                    memory_utilization, 2
                )
            },

            "allocation_status": {
                "FULL": full_allocations,
                "PARTIAL": partial_allocations,
                "UNMET": unmet_allocations
            },

            "priority_distribution": priority_counts
        }

    except FileNotFoundError as e:

        raise HTTPException(
            status_code=404,
            detail=str(e)
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Could not calculate metrics: {str(e)}"
        )


# ============================================================
# RUN OPTIMIZATION PIPELINE
# ============================================================

@app.post("/run-optimization")
def run_optimization():

    try:

        print("Starting ML → Scheduler pipeline...")

        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "src.integration.prediction_scheduler"
            ],
            cwd=str(PROJECT_ROOT),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=120
        )

        if result.returncode != 0:

            raise HTTPException(
                status_code=500,
                detail={
                    "message": "Optimization pipeline failed.",
                    "stdout": result.stdout,
                    "stderr": result.stderr
                }
            )

        # ----------------------------------------------------
        # Load newly generated allocation results
        # ----------------------------------------------------

        allocations = load_csv(ALLOCATIONS_FILE)

        return {
            "status": "success",
            "message": "ML prediction and resource allocation completed.",
            "tasks_processed": len(allocations),
            "output_file": "results/resource_allocation.csv",
            "pipeline_output": result.stdout
        }

    except subprocess.TimeoutExpired:

        raise HTTPException(
            status_code=504,
            detail="Optimization pipeline timed out."
        )

    except HTTPException:

        raise

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Optimization failed: {str(e)}"
        )