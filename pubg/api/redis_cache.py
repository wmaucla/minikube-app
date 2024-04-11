import json
import logging
import os
from typing import Dict

import cachetools.func
import redis
import tenacity
from redis.cluster import RedisCluster as Redis


@tenacity.retry(
    wait=tenacity.wait_exponential(min=0.1, max=1.0),
    stop=tenacity.stop_after_attempt(3),
    reraise=True,
)
async def write_redis(data: Dict[str, int]) -> None:
    """Writes data to Redis with exponential backoff retry mechanism.

    Args:
        data (Dict[str, int]): A dictionary containing keys and integer values to be written to Redis.

    Returns:
        None

    Raises:
        RetryError: If retries are exhausted and the operation still fails.
    """
    redis_client = Redis(
        host=os.environ["REDIS_HOST"],
        password=os.environ["REDIS_PASSWORD"],
        port=6379,
        decode_response=True,
    )  # type: ignore

    logging.info("Writing data to Redis")
    for key, val in data.items():
        encoded_str = json.dumps(val)
        redis_client.set(key, encoded_str)

    logging.info("Data written to Redis successfully")


@cachetools.func.ttl_cache(maxsize=100, ttl=300)  # implement a caching strategy
def fetch_redis(user_id: str) -> Dict[str, int] | None:
    """Fetches data from Redis with caching.

    Args:
        user_id (str): The ID of the user for which data is to be fetched.

    Returns:
        Optional[Dict[str, int]]: A dictionary containing the fetched data, or None if no data is found.

    Raises:
        RedisError: If an error occurs while fetching data from Redis.
    """
    redis_client = Redis(
        host=os.environ["REDIS_HOST"],
        password=os.environ["REDIS_PASSWORD"],
        port=6379,
        decode_response=True,
    )  # type: ignore

    try:
        data = redis_client.get(user_id)

        if data:
            decoded_data = json.loads(data.decode("utf-8"))  # type: ignore
            return decoded_data
        else:
            logging.info(f"No data found for the key {user_id}")

    except redis.exceptions.RedisError as e:
        # Handle Redis errors
        logging.error("An error occurred while fetching data from Redis: %s", e)

    except Exception as e:
        # Handle other exceptions
        logging.error("An unexpected error occurred: %s", e)

    return None
