import io
import time
import smbus
import threading
import RPi.GPIO as GPIO
from flask import Flask, render_template, jsonify, Response
from picamera2 import Picamera2
from picamera2.encoders import JpegEncoder
from picamera2.outputs import FileOutput

app = Flask(__name__)

bus = smbus.SMBus(1)

led_pin = 23
GPIO.setmode(GPIO.BCM)
GPIO.setup(led_pin, GPIO.OUT, initial=GPIO.LOW)

class StreamingOutput(io.BufferedIOBase):
    def __init__(self):
        self.frame = None
        self.condition = threading.Condition()

    def write(self, buf):
        with self.condition:
            self.frame = buf
            self.condition.notify_all()

def generate():
    while True:
        with output.condition:
            output.condition.wait()
            frame = output.frame
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

def read_sensor_data():
    bus.write_i2c_block_data(0x44, 0x2C, [0x06])
    time.sleep(0.5)
    data = bus.read_i2c_block_data(0x44, 0x00, 6)
    cTemp = ((((data[0] * 256.0) + data[1]) * 175) / 65535.0) - 45
    humidity = 100 * (data[3] * 256 + data[4]) / 65535.0
    return { 'temperature': round(cTemp, 2), 'humidity': round(humidity, 2) }

@app.route('/')
def index():
    return render_template('index.html', sensor_data=read_sensor_data())

@app.route('/get_sensor_data')
def get_sensor_data():
    return jsonify(read_sensor_data())
    
@app.route('/toggle_ir', methods=['POST'])
def toggle_ir():
    GPIO.output(led_pin, not GPIO.input(led_pin))
    return 'Success'

@app.route('/video_feed')
def video_feed():
    return Response(generate(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    picam2 = Picamera2()
    picam2.configure(picam2.create_video_configuration(main={"size": (640, 480)}))
    output = StreamingOutput()
    picam2.start_recording(JpegEncoder(), FileOutput(output))

    try:
        app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
    finally:
        picam2.stop_recording()
