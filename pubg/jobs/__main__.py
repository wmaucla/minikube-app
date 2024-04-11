import logging
import time

from pubg.config import MinioConfig
from pubg.jobs.config import PUBGConfig
from pubg.jobs.get_season_data import fetch_pubg_leaderboard
from pubg.jobs.write_minio import write_leaderboard_data_minio

if __name__ == "__main__":

    logging.info("Beginning job to fetch from pubg_leaderboard...")

    for server in PUBGConfig.SERVERS:
        for game_mode in PUBGConfig.GAME_MODE:

            logging.info(f"Beginning fetch for {server} in game mode {game_mode}")
            pubg_data = fetch_pubg_leaderboard(server=server, game_mode=game_mode)

            bucket_name = f"{MinioConfig.BUCKET_BASE_NAME}-{server}-{game_mode}"
            logging.info(f"Beginning write for {bucket_name}")
            write_leaderboard_data_minio(bucket_name=bucket_name, data=pubg_data)

            logging.info(f"Job completed for {bucket_name}")

            time.sleep(20)  # slow down requests

    logging.info("Completed job execution.")
