from datetime import datetime

from pydantic import BaseModel, field_validator

from pubg.jobs.config import PUBGConfig


class WriteRedisRequest(BaseModel):
    object_name: str
    game_mode: str
    server: str

    @field_validator("game_mode")
    def validate_game_mode(cls, v):
        if v not in PUBGConfig.GAME_MODE:
            raise ValueError(
                f"Invalid game mode: {v}. Must be one of {', '.join(PUBGConfig.GAME_MODE)}"
            )
        return v

    @field_validator("server")
    def validate_server(cls, v):
        if v not in PUBGConfig.SERVERS:
            raise ValueError(
                f"Invalid server: {v}. Must be one of {', '.join(PUBGConfig.SERVERS)}"
            )
        return v

    @field_validator("object_name")
    def validate_object_name(cls, v):
        # Split the filename using underscores
        parts = v.split("_")
        if len(parts) < 2:
            raise ValueError(
                f"Invalid object_name format: {v}. Files will contain a datetime"
            )
        try:
            # Attempt to parse the first part of the filename as a datetime object
            datetime.strptime(parts[1].replace(".json", ""), "%Y-%m-%d-%H-%M-%S")
        except ValueError:
            # If parsing fails, raise a validation error
            raise ValueError(
                f"Invalid object_name format: {v}. The datetime part must be in the format YYYY-MM-DD_HH-MM-SS"
            )
        return v


class UserDataRequest(BaseModel):
    user_id: str

    @field_validator("user_id")
    def validate_user_id_format(cls, v):
        # Ensure that user_id starts with "account." and has SOMETHING following it
        if not v.startswith("account.") or len(v) <= len("account."):
            raise ValueError("user_id must start with 'account.' followed by SOMETHING")
        return v


class UserDataResponse(BaseModel):
    user_id: str
    rank: int
    wins: int
    games_played: int


class GameModeRequest(BaseModel):
    game_mode: str
    server: str

    @field_validator("server")
    def validate_server(cls, v):
        if v not in PUBGConfig.SERVERS:
            raise ValueError(
                f"Invalid server: {v}. Must be one of {', '.join(PUBGConfig.SERVERS)}"
            )
        return v

    @field_validator("game_mode")
    def validate_game_mode(cls, v):
        if v not in PUBGConfig.GAME_MODE:
            raise ValueError(
                f"Invalid game mode: {v}. Must be one of {', '.join(PUBGConfig.GAME_MODE)}"
            )
        return v
