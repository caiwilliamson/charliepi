import io
import threading
from picamera2 import Picamera2
from picamera2.encoders import JpegEncoder
from picamera2.outputs import FileOutput

class Camera:
    def __init__(self):
        self._picam2 = Picamera2()
        self._output = StreamingOutput()

    def start(self):
        self._picam2.configure(self._picam2.create_video_configuration(main={"size": (640, 480)}))
        self._picam2.start_recording(JpegEncoder(), FileOutput(self._output))

    def stream(self):
        while True:
            with self._output.condition:
                self._output.condition.wait()
                frame = self._output.frame
            yield (
                b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n'
            )

    def stream_response(self):
        return self.stream(), 'multipart/x-mixed-replace; boundary=frame'

    def stop(self):
        self._picam2.stop_recording()

class StreamingOutput(io.BufferedIOBase):
    def __init__(self):
        self.frame = None
        self.condition = threading.Condition()

    def write(self, buf):
        with self.condition:
            self.frame = buf
            self.condition.notify_all()
