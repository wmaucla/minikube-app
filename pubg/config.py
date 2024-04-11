from pydantic_settings import BaseSettings


class _MinioConfig(BaseSettings):
    """Config for fetching from Minio"""

    MINIO_ROOT_USER: str = ""
    MINIO_ROOT_PASSWORD: str = ""
    MINIO_ENDPOINT: str = "localhost:9000"

    # The base name, will concat w/ season type
    BUCKET_BASE_NAME: str = "pubg-leaderboard-bucket"


MinioConfig = _MinioConfig()
