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

def convert_timestamp_column(series, column_name):
    """
    Convert either numeric or datetime timestamps
    into seconds.
    """

    # First try numeric timestamps
    numeric_values = pd.to_numeric(
        series,
        errors="coerce"
    )

    numeric_ratio = (
        numeric_values.notna().sum()
        / max(len(series), 1)
    )

    # If most values are numeric, determine the unit
    if numeric_ratio >= 0.8:

        median_timestamp = (
            numeric_values
            .dropna()
            .abs()
            .median()
        )

        if median_timestamp < 1e11:
            divisor = 1
            time_unit = "seconds"

        elif median_timestamp < 1e14:
            divisor = 1_000
            time_unit = "milliseconds"

        elif median_timestamp < 1e17:
            divisor = 1_000_000
            time_unit = "microseconds"

        else:
            divisor = 1_000_000_000
            time_unit = "nanoseconds"

        print(
            f"Detected {column_name} as numeric "
            f"timestamp: {time_unit}"
        )

        return numeric_values / divisor

    # Otherwise treat it as a datetime string
    datetime_values = pd.to_datetime(
        series,
        errors="coerce"
    )

    print(
        f"Detected {column_name} as datetime timestamp"
    )

    # Convert datetime to Unix seconds
    result = pd.Series(
        float("nan"),
        index=series.index
    )

    valid = datetime_values.notna()

    result.loc[valid] = (
        datetime_values.loc[valid]
        - pd.Timestamp("1970-01-01")
    ).dt.total_seconds()

    return result


df["start_time_seconds"] = convert_timestamp_column(
    df["start_time"],
    "start_time"
)


if "end_time" in df.columns:

    df["end_time_seconds"] = convert_timestamp_column(
        df["end_time"],
        "end_time"
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

# Keep end time if the input dataset contains it
if "end_time_seconds" in ml_df.columns:
    ml_columns.insert(
        2,
        "end_time_seconds"
    )


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