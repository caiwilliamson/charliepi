from flask import Flask, render_template, jsonify, Response
from peewee import SqliteDatabase

from sensor_data import SensorData
from camera import setup_camera, stream_camera, close_camera
from sht_30 import read_sht_30
from led import LED

app = Flask(__name__)

ir_led = LED(pin=23)
picam2, output = setup_camera()

@app.route('/')
def index():
    sensor_data = read_sht_30()
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
    return jsonify(read_sht_30())

@app.route('/toggle_ir', methods=['POST'])
def toggle_ir():
    ir_led.toggle()
    return Response(status=204)

@app.route('/video_feed')
def video_feed():
    return Response(
        stream_camera(output),
        mimetype='multipart/x-mixed-replace; boundary=frame'
    )

if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
    finally:
        picam2.stop_recording()
        ir_led.cleanup()
