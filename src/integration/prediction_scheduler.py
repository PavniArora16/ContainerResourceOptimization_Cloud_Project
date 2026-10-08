import pandas as pd
import sys
from src.config import (
    PREDICTION_FILE,
    ALLOCATION_FILE,
    TOTAL_CPU,
    TOTAL_MEMORY
)
# Make stdout UTF-8 compatible on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(
        encoding="utf-8",
        errors="replace"
    )

from src.scheduler.priority_manager import (
    assign_priority
)

from src.scheduler.resource_allocator import (
    allocate_resources
)


# --------------------------------------------------
# File paths
# --------------------------------------------------




# --------------------------------------------------
# Available cluster resources
# --------------------------------------------------



# --------------------------------------------------
# Load ML predictions
# --------------------------------------------------

print("----------------------------------------")
print("ML → SCHEDULER INTEGRATION")
print("----------------------------------------")

print("\nLoading ML predictions...")

df = pd.read_csv(PREDICTION_FILE)

print(
    f"Predictions loaded: {len(df):,}"
)


# --------------------------------------------------
# Create scheduling workloads
# --------------------------------------------------

workloads = []


# integration demonstration.

for index, row in df.iterrows():

    # Temporary priority mapping for testing.
    # Actual Google trace priority will be
    # integrated in the next stage.

    # Calculate priority from predicted resource demand.
# Higher CPU + memory demand receives higher priority.

    resource_score = (
        float(row["predicted_cpu"])
        + float(row["predicted_memory"])
    ) 

    priority = assign_priority(
        resource_score
    )

    workloads.append({

        "task_id": row["task_id"],

        "priority": priority,

        "predicted_cpu": float(
            row["predicted_cpu"]
        ),

        "predicted_memory": float(
            row["predicted_memory"]
        )
    })


# --------------------------------------------------
# Run resource allocator
# --------------------------------------------------

print("\nRunning resource allocator...")

allocations = allocate_resources(
    workloads,
    total_cpu=TOTAL_CPU,
    total_memory=TOTAL_MEMORY
)


# --------------------------------------------------
# Convert results to DataFrame
# --------------------------------------------------

allocation_df = pd.DataFrame(
    allocations
)


# --------------------------------------------------

# --------------------------------------------------

# --------------------------------------------------
# Calculate cumulative cluster utilization
# --------------------------------------------------

allocation_df["cluster_cpu_utilization"] = (
    allocation_df["allocated_cpu"].cumsum()
    / TOTAL_CPU
)

allocation_df["cluster_memory_utilization"] = (
    allocation_df["allocated_memory"].cumsum()
    / TOTAL_MEMORY
)


# --------------------------------------------------
# Save allocation results
# --------------------------------------------------

allocation_df.to_csv(
    ALLOCATION_FILE,
    index=False
)


# --------------------------------------------------
# Display summary
# --------------------------------------------------

total_allocated_cpu = (
    allocation_df["allocated_cpu"].sum()
)

total_allocated_memory = (
    allocation_df["allocated_memory"].sum()
)


print("\n----------------------------------------")
print("RESOURCE ALLOCATION COMPLETED")
print("----------------------------------------")

print(
    allocation_df.to_string(index=False)
)

print("\n----------------------------------------")
print("RESOURCE SUMMARY")
print("----------------------------------------")

print(
    f"Total CPU available: {TOTAL_CPU}"
)

print(
    f"Total CPU allocated: "
    f"{total_allocated_cpu:.4f}"
)

print(
    f"Total Memory available: {TOTAL_MEMORY}"
)

print(
    f"Total Memory allocated: "
    f"{total_allocated_memory:.4f}"
)

print(
    f"\nSaved to: {ALLOCATION_FILE}"
)