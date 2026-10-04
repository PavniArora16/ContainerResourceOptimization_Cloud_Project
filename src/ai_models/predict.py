import argparse
from pathlib import Path

import joblib
import pandas as pd


# --------------------------------------------------
# Paths
# --------------------------------------------------

CPU_MODEL = Path("results/models/cpu_model.pkl")
MEMORY_MODEL = Path("results/models/memory_model.pkl")

OUTPUT_FILE = Path("results/predictions.csv")


# --------------------------------------------------
# Model features
# --------------------------------------------------

FEATURES = [
    "previous_cpu_1",
    "previous_cpu_2",
    "previous_cpu_3",
    "previous_memory_1",
    "previous_memory_2",
    "previous_memory_3",
    "cpu_usage",
    "memory_usage",
    "time_gap_seconds",
]


# --------------------------------------------------
# Prediction
# --------------------------------------------------

def predict(input_file):

    print("----------------------------------------")
    print("RESOURCE DEMAND PREDICTION")
    print("----------------------------------------")

    print(f"\nLoading: {input_file}")

    df = pd.read_csv(input_file)

    print(f"Rows loaded: {len(df):,}")

    missing_columns = [
        column
        for column in FEATURES
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            "Missing required feature columns: "
            + ", ".join(missing_columns)
        )

    # Load trained models
    cpu_model = joblib.load(CPU_MODEL)
    memory_model = joblib.load(MEMORY_MODEL)

    # Remove rows that cannot be predicted
    prediction_df = df.dropna(
        subset=FEATURES
    ).copy()

    print(
        f"Rows available for prediction: "
        f"{len(prediction_df):,}"
    )

    # Prepare features
    X = prediction_df[FEATURES]

    # Generate predictions
    prediction_df["predicted_cpu"] = (
        cpu_model.predict(X)
    )

    prediction_df["predicted_memory"] = (
        memory_model.predict(X)
    )

    # Save results
    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    prediction_df.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print("\n----------------------------------------")
    print("PREDICTION COMPLETED")
    print("----------------------------------------")

    print(
        f"Predicted rows: "
        f"{len(prediction_df):,}"
    )

    print(
        f"Saved to: {OUTPUT_FILE}"
    )


# --------------------------------------------------
# Command-line interface
# --------------------------------------------------

if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="Predict CPU and memory demand"
    )

    parser.add_argument(
        "--input",
        default="dataset/processed/ml_ready_dataset.csv",
        help="ML-ready CSV file"
    )

    args = parser.parse_args()

    predict(
        Path(args.input)
    )