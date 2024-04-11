import os


class _Config:
    APP_VERSION = "0.1.0"
    APP_NAME = "PUBG App"
    APP_ENV = os.getenv("APP_ENV", "localhost")
    IS_DEBUG = APP_ENV != "production"

    def __str__(self) -> str:
        return f'Config: name="{self.APP_NAME}" version="{self.APP_VERSION}" env="{self.APP_ENV}"'


Config = _Config()
