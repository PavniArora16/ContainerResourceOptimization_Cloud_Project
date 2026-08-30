import pandas as pd

from src.scheduler.priority_manager import (
    assign_priority
)

from src.scheduler.resource_allocator import (
    allocate_resources
)


# --------------------------------------------------
# File paths
# --------------------------------------------------

PREDICTION_FILE = (
    "results/predictions.csv"
)

OUTPUT_FILE = (
    "results/resource_allocation.csv"
)


# --------------------------------------------------
# Available cluster resources
# --------------------------------------------------

TOTAL_CPU = 1.0
TOTAL_MEMORY = 1.0


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

# Use first 20 predictions for the
# integration demonstration.

for index, row in df.head(20).iterrows():

    # Temporary priority mapping for testing.
    # Actual Google trace priority will be
    # integrated in the next stage.

    priority_value = index % 12

    priority = assign_priority(
        priority_value
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
# Calculate utilization
# --------------------------------------------------

allocation_df["cluster_cpu_utilization"] = (
    allocation_df["allocated_cpu"]
    / TOTAL_CPU
)

allocation_df["cluster_memory_utilization"] = (
    allocation_df["allocated_memory"]
    / TOTAL_MEMORY
)


# --------------------------------------------------
# Save allocation results
# --------------------------------------------------

allocation_df.to_csv(
    OUTPUT_FILE,
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
    f"\nSaved to: {OUTPUT_FILE}"
)