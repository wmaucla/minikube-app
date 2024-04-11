import logging

import tenacity
from fastapi import APIRouter, HTTPException, Response
from minio.error import S3Error
from pydantic import ValidationError

from pubg.api.minio_cache import get_minio_data, get_minio_recent
from pubg.api.models import (
    GameModeRequest,
    UserDataRequest,
    UserDataResponse,
    WriteRedisRequest,
)
from pubg.api.redis_cache import fetch_redis, write_redis
from pubg.jobs.config import PUBGConfig

logging.basicConfig(level=logging.INFO)


router = APIRouter()


@router.get("/healthcheck", response_class=Response)
async def get_healthcheck() -> None:
    return None


@router.post("/refresh_all_data")
async def refresh_data() -> str:
    """Fetches the most recent data file for all combinations of game modes and servers,
    and writes them to Redis.

    Returns:
        str: A completion message indicating which combinations were refreshed.

    Raises:
        HTTPException: If no recent data is found for a combination.
    """

    output = []

    logging.info("Beginning to refresh data!")
    for server in PUBGConfig.SERVERS:
        logging.info(f"Beginning to refresh data from server {server}")
        for game_mode in PUBGConfig.GAME_MODE:
            logging.info(f"Beginning to refresh data for game mode {game_mode}")

            # Try and fetch the data file from the bucket
            most_recent_file_name = await get_minio_recent(
                game_mode=game_mode,
                server=server,
            )

            if (
                most_recent_file_name is None
            ):  # TODO - needs to be fixed to be less messy
                logging.info(f"No data found for {game_mode} {server}, skipping")
                continue  # move onto next combination

            # Fetch data from minio to write out
            try:
                data = await get_minio_data(
                    game_mode=game_mode,
                    file_name=most_recent_file_name,
                    server=server,
                )
            except S3Error:
                logging.warning(f"Failure to find data for {most_recent_file_name}!")
                continue

            # Call the write_redis function with retry logic
            try:
                await write_redis(data=data)
            except tenacity.RetryError as e:
                # If retry attempts are exhausted, raise HTTP 503 Service Unavailable
                raise HTTPException(
                    status_code=503, detail="Retry attempts exhausted"
                ) from e

            output.append(f"{game_mode}&{server}")
            logging.info(f"Refresh completed for {game_mode}")
        logging.info(f"Refresh completed for {server}")

    return "Completed refresh for:" + ";".join(output)


@router.get("/most_recent_data")
async def get_most_recent_data(request: GameModeRequest) -> str | None:
    """Fetches the most recent data file based on the specified game mode and server.

    Args:
        request (GameModeRequest): The request payload containing the game mode and server.

    Returns:
        Optional[str]: The most recent data file or None if no data is found.

    Raises:
        HTTPException: If the request payload is invalid or no recent data is found.
    """
    # Validate the request payload
    try:
        validated_request = GameModeRequest(**request.dict())
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Try and fetch the data file from the bucket
    try:
        data = await get_minio_recent(
            game_mode=validated_request.game_mode,
            server=validated_request.server,
        )
    except S3Error as e:
        raise HTTPException(status_code=400, detail="No recent data found!") from e

    return data


@router.post("/write_redis_data")
async def write_redis_data(request: WriteRedisRequest) -> None:
    """Writes data from redis to minio

    Args:
        request (WriteRedisRequest): The request containing the details of the data to be written.

    Raises:
        HTTPException: If there is an error in the request payload or fetching data from Minio.
        HTTPException: If retry attempts are exhausted while writing data to Redis.
    """

    # Validate the request payload
    try:
        validated_request = WriteRedisRequest(**request.dict())
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Try and fetch the data file from the bucket
    try:
        data = await get_minio_data(
            game_mode=validated_request.game_mode,
            file_name=validated_request.object_name,
            server=validated_request.server,
        )
    except S3Error as e:
        raise HTTPException(status_code=400, detail="Data file not found!") from e

    # Call the write_redis function with retry logic
    try:
        await write_redis(data=data)
    except tenacity.RetryError as e:
        # If retry attempts are exhausted, raise HTTP 503 Service Unavailable
        raise HTTPException(status_code=503, detail="Retry attempts exhausted") from e


@router.get("/get_user_data/{user_id}", response_model=UserDataResponse)
async def get_user_data(user_id: str) -> UserDataResponse:
    """Gets user data from Redis.

    Args:
        user_id (str): The ID of the user for which data is to be fetched.

    Returns:
        UserDataResponse: The response containing the user data.

    Raises:
        HTTPException: If there is an error while fetching user data from Redis.
        HTTPException: If the user data is not found or invalid.
    """
    # Validate the request payload
    try:
        UserDataRequest(user_id=user_id)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))

    try:
        data = fetch_redis(user_id=user_id)
    except Exception as e:
        # Log the exception
        logging.error("An unexpected error occurred: %s", e)
        # Raise an HTTP 500 error for Internal Server Error
        raise HTTPException(status_code=500, detail="Internal Server Error")

    if data:
        return UserDataResponse(user_id=user_id, **data)
    else:
        raise HTTPException(status_code=404, detail="User not found or invalid data")
