import os

import pytest


# Fixture to patch environment variable
@pytest.fixture(autouse=True)
def patch_env_variable():

    # Patch environment variable
    os.environ["REDIS_HOST"] = "test_value"

    # Yield to test
    yield
