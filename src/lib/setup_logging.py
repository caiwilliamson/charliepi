import logging
import os

from definitions import ROOT_DIR_NAME


def setup_logging(file_name):
    home_directory = os.path.expanduser("~")
    log_directory = f"{home_directory}/log/{ROOT_DIR_NAME}"
    log_file = os.path.join(log_directory, f"{file_name}.log")

    os.makedirs(log_directory, exist_ok=True)

    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - [%(levelname)s] - %(message)s",
        handlers=[logging.StreamHandler(), logging.FileHandler(log_file)],
    )
