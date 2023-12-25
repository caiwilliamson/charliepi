import io
import threading

from picamera2 import Picamera2
from picamera2.encoders import JpegEncoder
from picamera2.outputs import FileOutput


class Camera:
    def __init__(self):
        self._picam2 = Picamera2()
        self._output = self.StreamingOutput()

    def start(self):
        self._picam2.configure(
            self._picam2.create_video_configuration(main={"size": (1280, 960)})
        )
        self._picam2.start_recording(JpegEncoder(), FileOutput(self._output))

    def stream_response(self):
        return self._stream(), "multipart/x-mixed-replace; boundary=frame"

    def stop(self):
        self._picam2.stop_recording()

    def _stream(self):
        while True:
            with self._output._condition:
                self._output._condition.wait()
                frame = self._output._frame
            yield (b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n")

    class StreamingOutput(io.BufferedIOBase):
        def __init__(self):
            self._frame = None
            self._condition = threading.Condition()

        def write(self, buf):
            with self._condition:
                self._frame = buf
                self._condition.notify_all()
