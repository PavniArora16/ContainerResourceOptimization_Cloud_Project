# Backend

This folder will contain the API and orchestration logic that connects the prediction model's output to Kubernetes scheduling actions.

## Planned Contents
- REST API endpoints for serving predictions and scheduling status
- Integration logic with Kubernetes API (triggering HPA/VPA adjustments)
- Priority-tagging logic for deadline-critical vs. batch containers

## Tech Stack (planned)
Python (Flask/FastAPI) — to be finalized during implementation phase.


# Backend - Container Resource Optimization

The backend provides a REST API for the ML-based container resource
optimization system.

## Technology

- Python
- FastAPI
- Uvicorn
- Pandas

## Architecture

```text
ML Prediction
     |
     v
Prediction CSV
     |
     v
Resource Scheduler
     |
     v
Allocation CSV
     |
     v
FastAPI Backend
     |
     v
React Frontend