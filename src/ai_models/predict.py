import pandas as pd
import joblib

from pathlib import Path


# --------------------------------------------------
# Load models
# --------------------------------------------------

CPU_MODEL = Path(
    "results/models/cpu_model.pkl"
)

MEMORY_MODEL = Path(
    "results/models/memory_model.pkl"
)


cpu_model = joblib.load(CPU_MODEL)

memory_model = joblib.load(MEMORY_MODEL)


# --------------------------------------------------
# Example workload
# --------------------------------------------------

sample = pd.DataFrame({
    "previous_cpu_1": [0.20],
    "previous_cpu_2": [0.18],
    "previous_cpu_3": [0.15],

    "previous_memory_1": [0.30],
    "previous_memory_2": [0.28],
    "previous_memory_3": [0.25],

    "cpu_usage": [0.22],
    "memory_usage": [0.32],

    "time_gap_seconds": [5]
})


# --------------------------------------------------
# Make predictions
# --------------------------------------------------

predicted_cpu = cpu_model.predict(
    sample
)[0]

predicted_memory = memory_model.predict(
    sample
)[0]


# --------------------------------------------------
# Display prediction
# --------------------------------------------------

print("----------------------------------------")
print("RESOURCE DEMAND PREDICTION")
print("----------------------------------------")

print(
    f"Predicted CPU usage    : {predicted_cpu:.6f}"
)

print(
    f"Predicted Memory usage : {predicted_memory:.6f}"
)