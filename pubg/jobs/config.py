from typing import List

from pydantic_settings import BaseSettings


class _PUBGConfig(BaseSettings):
    """Config for fetching from PUBG"""

    BASE_URL: str = "https://api.pubg.com/shards"
    LEADERBOARD_URL: str = "https://api.pubg.com/shards/pc-na/leaderboards"

    SERVERS: List[str] = ["kakao", "psn", "stadia", "steam", "xbox"]
    GAME_MODE: List[str] = [
        "squad-fpp",
        "solo",
        "squad",
    ]  # limit to prevent too many requests

    PUBG_API_TOKEN: str = ""  # NEEDS TO BE SET LOCALLY

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


PUBGConfig = _PUBGConfig()
