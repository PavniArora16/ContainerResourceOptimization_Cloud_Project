import boto3
from pathlib import Path

AWS_REGION = "ap-southeast-2"
BUCKET_NAME = "container-resource-optimization"

s3_client = boto3.client(
    "s3",
    region_name=AWS_REGION
)


def upload_file(local_file, s3_key):
    """
    Upload a local file to the configured S3 bucket.
    """

    local_file = Path(local_file)

    if not local_file.exists():
        raise FileNotFoundError(
            f"File not found: {local_file}"
        )

    s3_client.upload_file(
        str(local_file),
        BUCKET_NAME,
        s3_key
    )

    print(
        f"Uploaded {local_file} -> "
        f"s3://{BUCKET_NAME}/{s3_key}"
    )


def upload_project_results():
    """
    Upload generated project results to their S3 folders.
    """

    files_to_upload = {
        "dataset/processed/ml_ready_dataset.csv":
            "processed/ml_ready_dataset.csv",

        "results/predictions.csv":
            "predictions/predictions.csv",

        "results/resource_allocation.csv":
            "allocations/resource_allocation.csv",

        "results/models/cpu_model.pkl":
            "models/cpu_model.pkl",

        "results/models/memory_model.pkl":
            "models/memory_model.pkl",
    }

    for local_file, s3_key in files_to_upload.items():
        upload_file(local_file, s3_key)

