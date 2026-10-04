import argparse
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent


def run_step(description, command):

    print("\n" + "=" * 50)
    print(description)
    print("=" * 50)

    result = subprocess.run(
        command,
        cwd=str(PROJECT_ROOT),
        text=True
    )

    if result.returncode != 0:
        raise RuntimeError(
            f"{description} failed."
        )


def main():

    parser = argparse.ArgumentParser(
        description=(
            "Run the complete container "
            "resource optimization pipeline."
        )
    )

    parser.add_argument(
        "--input",
        required=True,
        help="Path to the raw workload CSV file"
    )

    args = parser.parse_args()

    input_file = Path(args.input)

    if not input_file.exists():
        raise FileNotFoundError(
            f"Input dataset not found: {input_file}"
        )

    print("----------------------------------------")
    print("CONTAINER RESOURCE OPTIMIZATION PIPELINE")
    print("----------------------------------------")

    print(
        f"\nInput dataset: {input_file}"
    )

    # --------------------------------------------------
    # Step 1: Preprocessing
    # --------------------------------------------------

    run_step(
        "STEP 1/4 - GENERIC PREPROCESSING",
        [
            sys.executable,
            "-m",
            "src.ai_models.preprocessing",
            "--input",
            str(input_file)
        ]
    )

    # --------------------------------------------------
    # Step 2: Training
    # --------------------------------------------------

    run_step(
        "STEP 2/4 - MODEL TRAINING",
        [
            sys.executable,
            "-m",
            "src.ai_models.train"
        ]
    )

    # --------------------------------------------------
    # Step 3: Prediction
    # --------------------------------------------------

    run_step(
        "STEP 3/4 - RESOURCE PREDICTION",
        [
            sys.executable,
            "-m",
            "src.ai_models.predict"
        ]
    )

    # --------------------------------------------------
    # Step 4: Scheduling
    # --------------------------------------------------

    run_step(
        "STEP 4/4 - RESOURCE ALLOCATION",
        [
            sys.executable,
            "-m",
            "src.integration.prediction_scheduler"
        ]
    )

    print("\n" + "=" * 50)
    print("PIPELINE COMPLETED SUCCESSFULLY")
    print("=" * 50)

    print("\nGenerated outputs:")
    print(" - dataset/processed/ml_ready_dataset.csv")
    print(" - results/models/cpu_model.pkl")
    print(" - results/models/memory_model.pkl")
    print(" - results/predictions.csv")
    print(" - results/resource_allocation.csv")


if __name__ == "__main__":
    main()