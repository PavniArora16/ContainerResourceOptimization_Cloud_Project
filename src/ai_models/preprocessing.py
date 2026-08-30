import pandas as pd
from pathlib import Path


# --------------------------------------------------
# File paths
# --------------------------------------------------

INPUT_FILE = Path(
    "dataset/processed/smart_factory_workload_sample.csv"
)

OUTPUT_FILE = Path(
    "dataset/processed/ml_ready_dataset.csv"
)


# --------------------------------------------------
# Load dataset
# --------------------------------------------------

print("Loading dataset...")

df = pd.read_csv(INPUT_FILE)

print(f"Rows loaded: {len(df):,}")


# --------------------------------------------------
# Validate columns
# --------------------------------------------------

required_columns = [
    "start_time",
    "end_time",
    "job_id",
    "task_index",
    "machine_id",
    "cpu_usage",
    "memory_usage"
]

missing_columns = [
    column for column in required_columns
    if column not in df.columns
]

if missing_columns:
    raise ValueError(
        f"Missing columns: {missing_columns}"
    )


# --------------------------------------------------
# Create unique task ID
# --------------------------------------------------

df["task_id"] = (
    df["job_id"].astype(str)
    + "_"
    + df["task_index"].astype(str)
)


# --------------------------------------------------
# Convert timestamps
# Google trace timestamps are in microseconds
# --------------------------------------------------

df["start_time_seconds"] = (
    df["start_time"] / 1_000_000
)

df["end_time_seconds"] = (
    df["end_time"] / 1_000_000
)


# --------------------------------------------------
# Convert resource measurements to numeric
# --------------------------------------------------

df["cpu_usage"] = pd.to_numeric(
    df["cpu_usage"],
    errors="coerce"
)

df["memory_usage"] = pd.to_numeric(
    df["memory_usage"],
    errors="coerce"
)


# --------------------------------------------------
# Remove invalid resource measurements
# --------------------------------------------------

df = df.dropna(
    subset=[
        "task_id",
        "cpu_usage",
        "memory_usage"
    ]
)

df = df[
    (df["cpu_usage"] >= 0)
    & (df["memory_usage"] >= 0)
]


# --------------------------------------------------
# Sort each task chronologically
# --------------------------------------------------

df = df.sort_values(
    ["task_id", "start_time"]
).reset_index(drop=True)


# --------------------------------------------------
# Create historical CPU features
# --------------------------------------------------

df["previous_cpu_1"] = (
    df.groupby("task_id")["cpu_usage"]
    .shift(1)
)

df["previous_cpu_2"] = (
    df.groupby("task_id")["cpu_usage"]
    .shift(2)
)

df["previous_cpu_3"] = (
    df.groupby("task_id")["cpu_usage"]
    .shift(3)
)


# --------------------------------------------------
# Create historical memory features
# --------------------------------------------------

df["previous_memory_1"] = (
    df.groupby("task_id")["memory_usage"]
    .shift(1)
)

df["previous_memory_2"] = (
    df.groupby("task_id")["memory_usage"]
    .shift(2)
)

df["previous_memory_3"] = (
    df.groupby("task_id")["memory_usage"]
    .shift(3)
)


# --------------------------------------------------
# Create prediction targets
# --------------------------------------------------

df["next_cpu"] = (
    df.groupby("task_id")["cpu_usage"]
    .shift(-1)
)

df["next_memory"] = (
    df.groupby("task_id")["memory_usage"]
    .shift(-1)
)


# --------------------------------------------------
# Calculate time gap between observations
# --------------------------------------------------

df["time_gap_seconds"] = (
    df.groupby("task_id")["start_time_seconds"]
    .diff()
)


# --------------------------------------------------
# Keep rows with enough history and a future target
# --------------------------------------------------

ml_df = df.dropna(
    subset=[
        "previous_cpu_1",
        "previous_cpu_2",
        "previous_cpu_3",
        "previous_memory_1",
        "previous_memory_2",
        "previous_memory_3",
        "next_cpu",
        "next_memory"
    ]
).copy()


# --------------------------------------------------
# Select final ML columns
# --------------------------------------------------

ml_df = ml_df[
    [
        "task_id",
        "machine_id",
        "start_time_seconds",

        "previous_cpu_1",
        "previous_cpu_2",
        "previous_cpu_3",

        "previous_memory_1",
        "previous_memory_2",
        "previous_memory_3",

        "cpu_usage",
        "memory_usage",

        "time_gap_seconds",

        "next_cpu",
        "next_memory"
    ]
]


# --------------------------------------------------
# Remove invalid time gaps
# --------------------------------------------------

ml_df = ml_df[
    (ml_df["time_gap_seconds"] >= 0)
    & (ml_df["time_gap_seconds"].notna())
]


# --------------------------------------------------
# Save processed dataset
# --------------------------------------------------

ml_df.to_csv(
    OUTPUT_FILE,
    index=False
)


# --------------------------------------------------
# Display results
# --------------------------------------------------

print("\n----------------------------------------")
print("PREPROCESSING COMPLETED")
print("----------------------------------------")

print(
    f"Original rows: {len(df):,}"
)

print(
    f"ML-ready rows: {len(ml_df):,}"
)

print("\nColumns:")
for column in ml_df.columns:
    print(f" - {column}")

print("\nFirst 5 rows:")
print(ml_df.head())

print(
    f"\nSaved to: {OUTPUT_FILE}"
)