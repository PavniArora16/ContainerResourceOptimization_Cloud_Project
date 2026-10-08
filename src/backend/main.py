from pathlib import Path
import subprocess
import sys
import json
import pandas as pd
from fastapi import FastAPI, HTTPException, File, UploadFile, BackgroundTasks
import uuid
from fastapi.middleware.cors import CORSMiddleware
from src.config import TOTAL_CPU, TOTAL_MEMORY
from src.aws.s3_client import upload_file


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

RESULTS_DIR = PROJECT_ROOT / "results"

PREDICTIONS_FILE = RESULTS_DIR / "predictions.csv"
ALLOCATIONS_FILE = RESULTS_DIR / "resource_allocation.csv"
# ============================================================
# OPTIMIZATION JOB STATUS
# ============================================================

optimization_jobs = {}


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
            "allocations": json.loads(df.to_json(orient="records"))
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

        total_cpu_available = TOTAL_CPU
        total_memory_available = TOTAL_MEMORY

        # Peak simultaneous resource usage.
        # The allocator releases resources when tasks finish,
        # so cumulative sum is not a valid utilization measure.

        peak_cpu_utilization = (
            allocations["cluster_cpu_utilization"].max()
        )

        peak_memory_utilization = (
            allocations["cluster_memory_utilization"].max()
        )

        peak_cpu_allocated = (
            peak_cpu_utilization * total_cpu_available
        )

        peak_memory_allocated = (
            peak_memory_utilization * total_memory_available
        )

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

        not_allocated = int(
        status_counts.get("NOT_ALLOCATED", 0)
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
                    peak_cpu_allocated, 4
                ),
                "utilization_percent": round(
                    peak_cpu_utilization * 100, 2
                )
            },

            "memory": {
                "available": total_memory_available,
                "allocated": round(
                    peak_memory_allocated, 4
                ),
                "utilization_percent": round(
                    peak_memory_utilization * 100, 2
                )
            },

            "allocation_status": {
    "FULL": full_allocations,
    "PARTIAL": partial_allocations,
    "NOT_ALLOCATED": not_allocated
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
# BACKGROUND OPTIMIZATION
# ============================================================

def run_pipeline_background(job_id: str, input_file: Path):
    """
    Run the complete optimization pipeline in the background.
    """

    optimization_jobs[job_id] = {
        "status": "running",
        "message": "Optimization pipeline is running."
    }

    try:

        result = subprocess.run(
            [
                sys.executable,
                "run_pipeline.py",
                "--input",
                str(input_file)
            ],
            cwd=str(PROJECT_ROOT),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=1200
        )

        if result.returncode != 0:

            optimization_jobs[job_id] = {
                "status": "failed",
                "message": "Optimization pipeline failed.",
                "output": result.stdout,
                "error": result.stderr
            }

            return

                # Upload pipeline outputs to S3
        s3_uploads = []

        files_to_upload = [
            (
                PREDICTIONS_FILE,
                "predictions/predictions.csv"
            ),
            (
                ALLOCATIONS_FILE,
                "allocations/resource_allocation.csv"
            ),
            (
                RESULTS_DIR / "models" / "cpu_model.pkl",
                "models/cpu_model.pkl"
            ),
            (
                RESULTS_DIR / "models" / "memory_model.pkl",
                "models/memory_model.pkl"
            )
        ]

        for local_file, s3_key in files_to_upload:
            upload_result = upload_file(
                local_file,
                s3_key
            )

            if not upload_result["success"]:
                raise RuntimeError(
                    f"S3 upload failed for {local_file}: "
                    f"{upload_result.get('error', 'Unknown error')}"
                )

            s3_uploads.append({
                "file": str(local_file),
                "s3_key": s3_key,
                "success": True
            })

        optimization_jobs[job_id] = {
            "status": "completed",
            "message": "Optimization completed and results uploaded to S3.",
            "output": result.stdout,
            "s3_uploads": s3_uploads
        }

    except subprocess.TimeoutExpired:

        optimization_jobs[job_id] = {
            "status": "failed",
            "message": "Optimization pipeline timed out."
        }

    except Exception as e:

        optimization_jobs[job_id] = {
            "status": "failed",
            "message": str(e)
        }

# ============================================================
# RUN OPTIMIZATION PIPELINE
# ============================================================

# ============================================================
# RUN OPTIMIZATION PIPELINE
# ============================================================

@app.post("/run-optimization")
async def run_optimization(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...)
):

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No file was provided."
        )

    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(
            status_code=400,
            detail="Only CSV files are supported."
        )

    upload_dir = (
        PROJECT_ROOT
        / "dataset"
        / "raw"
        / "user_uploads"
    )

    upload_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    # Prevent directory traversal through uploaded filenames
    safe_filename = Path(file.filename).name

    input_file = upload_dir / safe_filename

    try:

        file_content = await file.read()

        with open(input_file, "wb") as f:
            f.write(file_content)

        job_id = str(uuid.uuid4())

        optimization_jobs[job_id] = {
            "status": "queued",
            "message": "Optimization job has been queued.",
            "filename": safe_filename
        }

        background_tasks.add_task(
            run_pipeline_background,
            job_id,
            input_file
        )

        return {
            "status": "started",
            "message": "Optimization started successfully.",
            "job_id": job_id,
            "filename": safe_filename
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Could not start optimization: {str(e)}"
        )
    # ============================================================
# OPTIMIZATION STATUS
# ============================================================

@app.get("/optimization-status/{job_id}")
def get_optimization_status(job_id: str):

    if job_id not in optimization_jobs:
        raise HTTPException(
            status_code=404,
            detail="Optimization job not found."
        )

    return optimization_jobs[job_id]