import time

import schedule
from flask import Flask, Response, jsonify, render_template

from src.lib.camera import Camera
from src.lib.healthchecks_pinger import HealthchecksPinger
from src.lib.led import LED
from src.lib.models import Sht30Reading
from src.lib.run_threaded import run_threaded
from src.lib.setup_logging import setup_logging
from src.lib.sht30 import Sht30

setup_logging("web_app")

app = Flask(__name__)
camera = Camera()
camera.start()
sht30 = Sht30()
ir_led = LED(pin=23)


@app.route("/")
def index():
    sensor_data = sht30.read()
    past_sensor_data = (
        Sht30Reading.select().limit(10).order_by(Sht30Reading.timestamp.desc()).dicts()
    )
    return render_template(
        "index.html", sensor_data=sensor_data, past_sensor_data=past_sensor_data
    )


@app.route("/get_sensor_data")
def get_sensor_data():
    sensor_data = sht30.read()
    return jsonify(sensor_data)


@app.route("/toggle_ir", methods=["POST"])
def toggle_ir():
    ir_led.toggle()
    return Response(status=204)


@app.route("/video_feed")
def video_feed():
    stream, mimetype = camera.stream_response()
    return Response(stream, mimetype=mimetype)


def run_scheduled_tasks():
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    try:
        healthchecks_pinger = HealthchecksPinger(slug="web-app")
        schedule.every(2).minutes.do(run_threaded, healthchecks_pinger.ping)

        run_threaded(run_scheduled_tasks)

        app.run(host="0.0.0.0", port=5000, debug=False, threaded=True)
    finally:
        camera.stop()
        ir_led.cleanup()
