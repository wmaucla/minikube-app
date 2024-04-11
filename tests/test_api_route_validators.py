import pytest
from pydantic import ValidationError

from pubg.api.models import (
    GameModeRequest,
    UserDataRequest,
    UserDataResponse,
    WriteRedisRequest,
)


@pytest.mark.parametrize(
    "object_name, expected_valid",
    [
        ("data_2022-03-25-12-30-45.json", True),
        (
            "2022-03-25-12-30-45_data.json",
            False,
        ),  # Invalid case with datetime part elsewhere
        ("2022-03-25-12-30-45", False),  # Data needs to be part of the name
        ("invalid_format", False),  # Invalid case with no datetime part
    ],
)
def test_object_name_validation(object_name, expected_valid) -> None:
    if expected_valid:
        # If the object name is expected to be valid, there should be no validation error
        request = WriteRedisRequest(
            object_name=object_name, server="kakao", game_mode="squad-fpp"
        )
        assert request.object_name == object_name
    else:
        # If the object name is expected to be invalid, a validation error should be raised
        with pytest.raises(ValidationError):
            WriteRedisRequest(
                object_name=object_name, server="kakao", game_mode="squad-fpp"
            )


def test_game_mode() -> None:

    object_name = "data_2022-03-25-12-30-45.json"

    # If nothing wrong, ignore
    WriteRedisRequest(object_name=object_name, server="kakao", game_mode="squad-fpp")

    with pytest.raises(ValidationError):
        WriteRedisRequest(
            object_name=object_name, server="kakao", game_mode="not-a-valid-name"
        )


def test_server() -> None:

    object_name = "data_2022-03-25-12-30-45.json"

    # If nothing wrong, ignore
    WriteRedisRequest(object_name=object_name, server="kakao", game_mode="squad-fpp")

    with pytest.raises(ValidationError):
        WriteRedisRequest(object_name=object_name, server="abc", game_mode="squad-fpp")


@pytest.mark.parametrize(
    "user_id, rank, wins, games_played, expected_valid",
    [
        ("account.user123", 1, 10, 100, True),
        ("account.user123", 1, 10.5, 100, False),  # Invalid case with wins as a float
    ],
)
def test_user_data_response_validation(
    user_id, rank, wins, games_played, expected_valid
):
    if expected_valid:
        # If all fields are expected to be valid, there should be no validation error
        UserDataResponse(
            user_id=user_id, rank=rank, wins=wins, games_played=games_played
        )
    else:
        # If any field is expected to be invalid, a validation error should be raised
        with pytest.raises(ValueError):
            UserDataResponse(
                user_id=user_id, rank=rank, wins=wins, games_played=games_played
            )


@pytest.mark.parametrize(
    "user_id, expected_valid",
    [
        ("account.user123", True),
        ("user123", False),  # Invalid case with user_id not starting with "account."
        ("account.user_123", True),  # Valid case with user_id containing underscore
        ("account.", False),  # Needs a hash value at the end
    ],
)
def test_user_id_format_validation(user_id, expected_valid):
    if expected_valid:
        # If the user_id is expected to be valid, there should be no validation error
        UserDataRequest(user_id=user_id)
    else:
        # If the user_id is expected to be invalid, a validation error should be raised
        with pytest.raises(ValueError):
            UserDataRequest(user_id=user_id)


def test_game_mode_req() -> None:

    # If nothing wrong, ignore
    GameModeRequest(server="kakao", game_mode="squad-fpp")

    with pytest.raises(ValidationError):
        GameModeRequest(server="abc", game_mode="squad-fpp")

    with pytest.raises(ValidationError):
        GameModeRequest(server="kakao", game_mode="abc")
