import argparse
from pathlib import Path
import pandas as pd


# --------------------------------------------------
# Command-line input
# --------------------------------------------------

parser = argparse.ArgumentParser(
    description="Preprocess a raw workload dataset"
)

parser.add_argument(
    "--input",
    required=True,
    help="Path to raw workload CSV"
)

args = parser.parse_args()

INPUT_FILE = Path(args.input)

OUTPUT_FILE = Path(
    "dataset/processed/ml_ready_dataset.csv"
)


# --------------------------------------------------
# Column aliases
# --------------------------------------------------

COLUMN_ALIASES = {

    "start_time": [
        "start_time",
        "timestamp",
        "time",
        "start",
        "start_timestamp"
    ],

    "end_time": [
        "end_time",
        "end",
        "end_timestamp"
    ],

    "job_id": [
        "job_id",
        "job",
        "task_id",
        "task",
        "workload_id"
    ],

    "task_index": [
        "task_index",
        "task_number",
        "task_idx",
        "index"
    ],

    "machine_id": [
        "machine_id",
        "machine",
        "node_id",
        "node",
        "server_id",
        "host_id"
    ],

    "cpu_usage": [
        "cpu_usage",
        "cpu",
        "cpu_utilization",
        "cpu_util",
        "cpu_percent"
    ],

    "memory_usage": [
        "memory_usage",
        "memory",
        "memory_utilization",
        "memory_util",
        "ram_usage",
        "memory_percent"
    ]
}


# --------------------------------------------------
# Find matching column
# --------------------------------------------------

def find_column(columns, aliases):

    normalized = {
        str(column).strip().lower(): column
        for column in columns
    }

    for alias in aliases:

        if alias in normalized:
            return normalized[alias]

    return None


# --------------------------------------------------
# Detect columns automatically
# --------------------------------------------------

def detect_columns(df):

    detected = {}

    for standard_name, aliases in COLUMN_ALIASES.items():

        detected[standard_name] = find_column(
            df.columns,
            aliases
        )

    return detected


# --------------------------------------------------
# Load dataset
# --------------------------------------------------

print("----------------------------------------")
print("GENERIC WORKLOAD PREPROCESSING")
print("----------------------------------------")

print(f"\nLoading: {INPUT_FILE}")

if not INPUT_FILE.exists():

    raise FileNotFoundError(
        f"Input dataset not found: {INPUT_FILE}"
    )

df = pd.read_csv(INPUT_FILE)

print(
    f"Rows loaded: {len(df):,}"
)


# --------------------------------------------------
# Detect columns
# --------------------------------------------------

detected = detect_columns(df)

print("\nDetected columns:")

for name, column in detected.items():

    print(
        f" - {name}: {column}"
    )


# --------------------------------------------------
# Validate required resource columns
# --------------------------------------------------

if detected["cpu_usage"] is None:

    raise ValueError(
        "Could not detect CPU usage column. "
        "Expected a column such as "
        "'cpu', 'cpu_usage' or 'cpu_utilization'."
    )

if detected["memory_usage"] is None:

    raise ValueError(
        "Could not detect memory usage column. "
        "Expected a column such as "
        "'memory', 'memory_usage' or 'ram_usage'."
    )

if detected["start_time"] is None:

    raise ValueError(
        "Could not detect time column. "
        "Expected a column such as "
        "'timestamp', 'start_time' or 'time'."
    )


# --------------------------------------------------
# Rename detected columns
# --------------------------------------------------

rename_map = {

    column: standard_name

    for standard_name, column
    in detected.items()

    if column is not None
}

df = df.rename(
    columns=rename_map
)


# --------------------------------------------------
# Create task ID
# --------------------------------------------------

if (
    "job_id" in df.columns
    and "task_index" in df.columns
):

    df["task_id"] = (
        df["job_id"].astype(str)
        + "_"
        + df["task_index"].astype(str)
    )

elif "job_id" in df.columns:

    df["task_id"] = (
        df["job_id"].astype(str)
    )

elif "task_index" in df.columns:

    df["task_id"] = (
        df["task_index"].astype(str)
    )

else:

    # If no task identifier exists,
    # create one from row groups.
    df["task_id"] = (
        "task_"
        + df.index.astype(str)
    )


# --------------------------------------------------
# Convert resource values
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
# Convert timestamps
# --------------------------------------------------

df["start_time"] = pd.to_numeric(
    df["start_time"],
    errors="coerce"
)

if "end_time" in df.columns:

    df["end_time"] = pd.to_numeric(
        df["end_time"],
        errors="coerce"
    )


# --------------------------------------------------
# Automatically determine timestamp scale
# --------------------------------------------------

median_timestamp = (
    df["start_time"]
    .dropna()
    .abs()
    .median()
)

# Timestamp conversion
#
# This dataset uses microseconds.
# The CLI can later allow users to explicitly specify
# seconds, milliseconds, microseconds, or nanoseconds.

time_unit = "microseconds"

if time_unit == "nanoseconds":
    divisor = 1_000_000_000
elif time_unit == "microseconds":
    divisor = 1_000_000
elif time_unit == "milliseconds":
    divisor = 1_000
elif time_unit == "seconds":
    divisor = 1
else:
    raise ValueError(f"Unsupported time unit: {time_unit}")

print(
    f"Detected timestamp divisor: {divisor} "
    f"({time_unit})"
)


df["start_time_seconds"] = (
    df["start_time"]
    / divisor
)


if "end_time" in df.columns:

    df["end_time_seconds"] = (
        df["end_time"]
        / divisor
    )


print(
    f"\nDetected timestamp divisor: "
    f"{divisor}"
)


# --------------------------------------------------
# Remove invalid resource measurements
# --------------------------------------------------

df = df.dropna(
    subset=[
        "task_id",
        "start_time_seconds",
        "cpu_usage",
        "memory_usage"
    ]
)

df = df[
    (df["cpu_usage"] >= 0)
    & (df["memory_usage"] >= 0)
]


# --------------------------------------------------
# Sort chronologically
# --------------------------------------------------

# --------------------------------------------------
# Sort chronologically by machine
# --------------------------------------------------

df = df.sort_values(
    ["machine_id", "start_time_seconds"]
).reset_index(drop=True)


# --------------------------------------------------
# Historical CPU features
# --------------------------------------------------

df["previous_cpu_1"] = (
    df.groupby("machine_id")["cpu_usage"]
    .shift(1)
)

df["previous_cpu_2"] = (
    df.groupby("machine_id")["cpu_usage"]
    .shift(2)
)

df["previous_cpu_3"] = (
    df.groupby("machine_id")["cpu_usage"]
    .shift(3)
)


# --------------------------------------------------
# Historical memory features
# --------------------------------------------------

df["previous_memory_1"] = (
    df.groupby("machine_id")["memory_usage"]
    .shift(1)
)

df["previous_memory_2"] = (
    df.groupby("machine_id")["memory_usage"]
    .shift(2)
)

df["previous_memory_3"] = (
    df.groupby("machine_id")["memory_usage"]
    .shift(3)
)


# --------------------------------------------------
# Prediction targets
# --------------------------------------------------

df["next_cpu"] = (
    df.groupby("machine_id")["cpu_usage"]
    .shift(-1)
)

df["next_memory"] = (
    df.groupby("machine_id")["memory_usage"]
    .shift(-1)
)


# --------------------------------------------------
# Time gap
# --------------------------------------------------

df["time_gap_seconds"] = (
    df.groupby("machine_id")["start_time_seconds"]
    .diff()
)


# --------------------------------------------------
# Keep rows usable for ML
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
# Final ML dataset
# --------------------------------------------------

ml_columns = [
    "task_id",
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


ml_df = ml_df[
    ml_columns
]


# --------------------------------------------------
# Remove invalid time gaps
# --------------------------------------------------

ml_df = ml_df[
    (ml_df["time_gap_seconds"] >= 0)
    & (ml_df["time_gap_seconds"].notna())
]


# --------------------------------------------------
# Save
# --------------------------------------------------

OUTPUT_FILE.parent.mkdir(
    parents=True,
    exist_ok=True
)

ml_df.to_csv(
    OUTPUT_FILE,
    index=False
)


# --------------------------------------------------
# Summary
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

print(
    f"\nSaved to: {OUTPUT_FILE}"
)