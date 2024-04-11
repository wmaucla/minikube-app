import logging
from typing import Any, Dict, Optional

import requests

from pubg.jobs.config import PUBGConfig

# Configure logging
logging.basicConfig(level=logging.INFO)  # Set logging level to INFO


# @tenacity.retry(
#     wait=tenacity.wait_exponential(min=0.1, max=1.0),
#     stop=tenacity.stop_after_attempt(5),
#     reraise=True,
# )
def fetch_pubg_cur_season(server: str, url: Optional[str] = None) -> Any:
    """
    Fetches the current PUBG season ID.

    Args:
        server: the server being evaluated
        url (str, optional): The URL for the PUBG season data endpoint.
            If not provided, default is fetched from PUBGConfig.

    Returns:
        str: The ID of the current season.
            Returns None if the current season is not found or there's an error.
    """

    if url is None:
        url = PUBGConfig.BASE_URL

    url = f"{url}/{server}/seasons"

    headers = {
        "accept": "application/vnd.api+json",
        "Authorization": f"Bearer {PUBGConfig.PUBG_API_TOKEN}",
    }

    response = requests.get(url, headers=headers)
    response.raise_for_status()  # Raise an exception for bad response status
    data = response.json()

    # Iterate over the items in the 'data' list
    for item in data.get("data", []):
        attributes = item.get("attributes", {})
        if attributes.get("isCurrentSeason", False):
            cur_season_id = item["id"]
            logging.info(f"Current season ID found: {cur_season_id}")
            return cur_season_id

    logging.warning("Current season not found.")
    return None


# @tenacity.retry(
#     wait=tenacity.wait_exponential(
#         min=0.1, max=1.0
#     ),  # Exponential backoff wait strategy
#     stop=tenacity.stop_after_attempt(3),  # Retry 3 times
#     reraise=True,  # Reraise exceptions after retries
# )
def fetch_pubg_leaderboard(
    server: str, game_mode: str, url: str = PUBGConfig.LEADERBOARD_URL
) -> Dict[str, Dict[str, str]]:
    """
    Fetches PUBG leaderboard data.

    Args:
        server (str): The PUBG server type (e.g., "xbox", "steam).
        game_mode (str): The PUBG game mode type (e.g., "squad", "duo", "solo").
        url (str, optional): The base URL for PUBG leaderboard. Defaults to PUBGConfig.LEADERBOARD_URL.

    Returns:
        Dict[str, Dict[str, str]]: A dictionary containing player IDs as keys and their leaderboard details as values.
    """

    headers = {
        "accept": "application/vnd.api+json",
        "Authorization": f"Bearer {PUBGConfig.PUBG_API_TOKEN}",
    }

    logging.info(f"Fetching PUBG leaderboard for: {server}")

    # Fetch the current season ID
    cur_season_id = fetch_pubg_cur_season(server=server)

    if cur_season_id is None:
        logging.error(
            "Failed to fetch current PUBG season ID. Aborting leaderboard fetch."
        )
        return {}

    # Construct the URL with the current season ID and season type
    url = f"{url}/{cur_season_id}/{game_mode}"

    response = requests.get(url, headers=headers)
    response.raise_for_status()
    data = response.json()

    # If no data in current season / not active
    if "included" not in data or len(data.get("included", [])) != 500:
        logging.info(f"Current season not active game mode {game_mode} for {server}")
        return {}

    # Extract player details from the response
    player_dict = {}
    for player in data.get("included", []):
        details = player.get("attributes", {})
        player_dict[player["id"]] = {
            "rank": details.get("rank"),
            "wins": details["stats"].get("wins"),
            "games_played": details["stats"].get("games"),
        }

    return player_dict
