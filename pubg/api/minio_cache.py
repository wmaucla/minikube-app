import json
import logging
from typing import Dict

from minio import Minio
from minio.error import S3Error

from pubg.config import MinioConfig


async def get_minio_data(game_mode: str, file_name: str, server: str) -> Dict[str, int]:
    """Fetches data from Minio object storage.

    Args:
        game_mode (str): The game mode for which data is to be fetched.
        file_name (str): The name of the file containing the data.
        server (str): The name of the server to fetch from

    Returns:
        Dict[str, int]: A dictionary containing the fetched data.

    Raises:
        S3Error: If there is an error fetching data from Minio.
    """
    minio_client = Minio(
        endpoint=MinioConfig.MINIO_ENDPOINT,
        access_key=MinioConfig.MINIO_ROOT_USER,
        secret_key=MinioConfig.MINIO_ROOT_PASSWORD,
        secure=False,  # no TLS encryption
    )

    bucket_name = f"pubg-leaderboard-bucket-{server}-{game_mode}"

    logging.info("Fetching data from Minio")
    try:
        response = minio_client.get_object(
            bucket_name=bucket_name, object_name=file_name
        )
        content = response.read().decode("utf-8")
    except S3Error as e:
        logging.error(f"Error fetching data from Minio: {e}")
        raise

    data = json.loads(content)
    return data


async def get_minio_recent(server: str, game_mode: str) -> str | None:
    """
    Retrieve the most recent file object from a MinIO bucket.

    Args:
        server (str): The server identifier.
        game_mode (str): The game mode.

    Returns:
        str: The name of the most recent file object found in the MinIO bucket.

    Raises:
        S3Error: If an error occurs while communicating with MinIO.
    """
    minio_client = Minio(
        endpoint=MinioConfig.MINIO_ENDPOINT,
        access_key=MinioConfig.MINIO_ROOT_USER,
        secret_key=MinioConfig.MINIO_ROOT_PASSWORD,
        secure=False,  # no TLS encryption
    )

    bucket_name = f"pubg-leaderboard-bucket-{server}-{game_mode}"

    logging.info(f"Looking for most recent data from {bucket_name}")

    most_recent_file = None

    try:
        # List objects in the bucket
        objects = minio_client.list_objects(bucket_name, recursive=True)

        # Iterate through the objects and find the most recent one

        for obj in objects:
            if (
                most_recent_file is None
                or obj.last_modified > most_recent_file.last_modified
            ):
                most_recent_file = obj

        if most_recent_file:  # get the str name of the file
            most_recent_file = most_recent_file.object_name

    except S3Error as err:
        logging.warning(f"MinIO error: {err}")

    return most_recent_file
