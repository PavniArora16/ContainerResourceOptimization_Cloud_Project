import pandas as pd
import joblib

from pathlib import Path

from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error
from sklearn.metrics import mean_squared_error
from sklearn.metrics import r2_score


# --------------------------------------------------
# File paths
# --------------------------------------------------

DATA_FILE = Path(
    "dataset/processed/ml_ready_dataset.csv"
)

MODEL_DIR = Path("results/models")

MODEL_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# --------------------------------------------------
# Load data
# --------------------------------------------------

print("Loading ML-ready dataset...")

df = pd.read_csv(DATA_FILE)

print(f"Rows: {len(df):,}")


# --------------------------------------------------
# Define input features
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

    "time_gap_seconds"
]


# --------------------------------------------------
# Define targets
# --------------------------------------------------

CPU_TARGET = "next_cpu"
MEMORY_TARGET = "next_memory"


# --------------------------------------------------
# Sort chronologically
# --------------------------------------------------

df = df.sort_values(
    "start_time_seconds"
).reset_index(drop=True)


# --------------------------------------------------
# Time-based train/test split
# --------------------------------------------------

split_index = int(
    len(df) * 0.8
)

train_df = df.iloc[:split_index]
test_df = df.iloc[split_index:]


print(
    f"Training rows: {len(train_df):,}"
)

print(
    f"Testing rows: {len(test_df):,}"
)


# --------------------------------------------------
# Prepare training data
# --------------------------------------------------

X_train = train_df[FEATURES]

y_cpu_train = train_df[CPU_TARGET]

y_memory_train = train_df[MEMORY_TARGET]


# --------------------------------------------------
# Prepare testing data
# --------------------------------------------------

X_test = test_df[FEATURES]

y_cpu_test = test_df[CPU_TARGET]

y_memory_test = test_df[MEMORY_TARGET]


# --------------------------------------------------
# CPU model
# --------------------------------------------------

print("\nTraining CPU model...")

cpu_model = RandomForestRegressor(
    n_estimators=100,
    max_depth=15,
    random_state=42,
    n_jobs=-1
)

cpu_model.fit(
    X_train,
    y_cpu_train
)


# --------------------------------------------------
# Memory model
# --------------------------------------------------

print("Training memory model...")

memory_model = RandomForestRegressor(
    n_estimators=100,
    max_depth=15,
    random_state=42,
    n_jobs=-1
)

memory_model.fit(
    X_train,
    y_memory_train
)


# --------------------------------------------------
# Predictions
# --------------------------------------------------

cpu_predictions = cpu_model.predict(
    X_test
)

memory_predictions = memory_model.predict(
    X_test
)


# --------------------------------------------------
# Evaluation function
# --------------------------------------------------

def evaluate_model(actual, predicted, name):

    mae = mean_absolute_error(
        actual,
        predicted
    )

    rmse = mean_squared_error(
        actual,
        predicted
    ) ** 0.5

    r2 = r2_score(
        actual,
        predicted
    )

    print(f"\n{name} Prediction Results")

    print(f"MAE  : {mae:.6f}")
    print(f"RMSE : {rmse:.6f}")
    print(f"R²   : {r2:.6f}")

    return mae, rmse, r2


# --------------------------------------------------
# Evaluate models
# --------------------------------------------------

cpu_metrics = evaluate_model(
    y_cpu_test,
    cpu_predictions,
    "CPU"
)

memory_metrics = evaluate_model(
    y_memory_test,
    memory_predictions,
    "Memory"
)


# --------------------------------------------------
# Save models
# --------------------------------------------------

joblib.dump(
    cpu_model,
    MODEL_DIR / "cpu_model.pkl"
)

joblib.dump(
    memory_model,
    MODEL_DIR / "memory_model.pkl"
)


# --------------------------------------------------
# Save test predictions
# --------------------------------------------------

results = test_df[
    [
        "task_id",
        "start_time_seconds",
        "cpu_usage",
        "memory_usage",
        "next_cpu",
        "next_memory"
    ]
].copy()

results["predicted_cpu"] = cpu_predictions

results["predicted_memory"] = memory_predictions

results.to_csv(
    "results/predictions.csv",
    index=False
)


print("\n----------------------------------------")
print("TRAINING COMPLETED")
print("----------------------------------------")

print("Models saved in results/models/")
print("Predictions saved in results/predictions.csv")