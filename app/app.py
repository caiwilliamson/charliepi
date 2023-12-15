from flask import Flask, render_template, jsonify, Response
from peewee import SqliteDatabase

from sensor_data import SensorData
from camera import Camera
from sht_30 import SHT30
from led import LED

app = Flask(__name__)

camera = Camera()
camera.start()

sht_30 = SHT30()
ir_led = LED(pin=23)

@app.route('/')
def index():
    sensor_data = sht_30.read()
    past_sensor_data = (
        SensorData
        .select()
        .limit(10)
        .order_by(SensorData.timestamp.desc())
        .dicts()
    )
    return render_template(
        'index.html',
        sensor_data=sensor_data,
        past_sensor_data=past_sensor_data
    )

@app.route('/get_sensor_data')
def get_sensor_data():
    sensor_data = sht_30.read()
    return jsonify(sensor_data)

@app.route('/toggle_ir', methods=['POST'])
def toggle_ir():
    ir_led.toggle()
    return Response(status=204)

@app.route('/video_feed')
def video_feed():
    stream, mimetype = camera.stream_response()
    return Response(stream, mimetype=mimetype)

if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
    finally:
        camera.stop()
        ir_led.cleanup()
