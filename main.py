import os

from definitions import ROOT_DIR
from src.lib.daemonize import Daemonize

if __name__ == '__main__':
    Daemonize(
        file_path=os.path.join(ROOT_DIR, "src/sht30_recorder.py"),
        service_name="sht30_recorder",
        service_description="Record temperature and humidity readings from an SHT30 sensor"
    )
    Daemonize(
        file_path=os.path.join(ROOT_DIR, "src/web_app.py"),
        service_name="charlie_pi_web",
        service_description="Charlie Pi web app"
    )
