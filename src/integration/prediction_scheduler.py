import pandas as pd

from src.scheduler.priority_manager import (
    Priority,
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


# --------------------------------------------------
# Load ML predictions
# --------------------------------------------------

print("Loading ML predictions...")

df = pd.read_csv(PREDICTION_FILE)

print(
    f"Predictions loaded: {len(df):,}"
)


# --------------------------------------------------
# Create scheduling workload
# --------------------------------------------------

workloads = []


for index, row in df.head(20).iterrows():

    # Temporary priority for integration testing.
    # Actual trace priority will be integrated later.
    priority_value = index % 12

    priority = assign_priority(
        priority_value
    )

    workloads.append({
        "task_id": row["task_id"],

        "priority": priority,

        "predicted_cpu": row["predicted_cpu"],

        "predicted_memory": row["predicted_memory"]
    })


# --------------------------------------------------
# Available resources
# --------------------------------------------------

TOTAL_CPU = 1.0

TOTAL_MEMORY = 1.0


# --------------------------------------------------
# Run resource allocator
# --------------------------------------------------

allocations = allocate_resources(
    workloads,
    total_cpu=TOTAL_CPU,
    total_memory=TOTAL_MEMORY
)


# --------------------------------------------------
# Convert result to DataFrame
# --------------------------------------------------

allocation_df = pd.DataFrame(
    allocations
)


# --------------------------------------------------
# Save allocation results
# --------------------------------------------------

output_file = (
    "results/resource_allocation.csv"
)

allocation_df.to_csv(
    output_file,
    index=False
)


# --------------------------------------------------
# Display results
# --------------------------------------------------

print("\n----------------------------------------")
print("RESOURCE ALLOCATION COMPLETED")
print("----------------------------------------")

print(
    allocation_df.to_string(index=False)
)

print(
    f"\nSaved to: {output_file}"
)