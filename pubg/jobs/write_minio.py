import json
import logging
from datetime import datetime
from io import BytesIO
from typing import Dict

import tenacity
from minio import Minio
from minio.error import S3Error

from pubg.config import MinioConfig


@tenacity.retry(
    wait=tenacity.wait_exponential(
        min=0.1, max=1.0
    ),  # Exponential backoff wait strategy
    stop=tenacity.stop_after_attempt(3),  # Retry 3 times
    reraise=True,  # Reraise exceptions after retries
)
def write_leaderboard_data_minio(
    bucket_name: str, data: Dict[str, Dict[str, str]]
) -> None:

    minio_client = Minio(
        endpoint=MinioConfig.MINIO_ENDPOINT,
        access_key=MinioConfig.MINIO_ROOT_USER,
        secret_key=MinioConfig.MINIO_ROOT_PASSWORD,
        secure=False,  # no TLS encryption
    )

    # Get the current date
    current_date = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")

    object_name = f"data_{current_date}.json"

    # Early exit if data is blank
    if data == {}:
        logging.info("Not writing any data, data is not active")
        return

    # Make the bucket if it doesn't exist.
    found = minio_client.bucket_exists(bucket_name)
    if not found:
        minio_client.make_bucket(bucket_name)
        logging.info(f"Created bucket {bucket_name}")

    # Convert dictionary to JSON string
    json_data = json.dumps(data).encode("utf-8")

    # Write JSON data to the MinIO bucket
    try:
        minio_client.put_object(
            bucket_name=bucket_name,
            object_name=object_name,
            data=BytesIO(json_data),
            length=len(json_data),
            content_type="application/json",
        )
        logging.info(f"JSON data uploaded to {bucket_name}/{object_name} successfully.")
    except S3Error as e:
        logging.warning(f"Error: {e}")
