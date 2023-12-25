import io
import threading

import cv2
import numpy as np
from picamera2 import Picamera2
from picamera2.encoders import JpegEncoder
from picamera2.outputs import FileOutput


class Camera:
    def __init__(self):
        self._picam2 = Picamera2()
        self._output = self.StreamingOutput()
        self.object_detection_enabled = True

    def start(self):
        self.class_names = []
        class_file = "/home/cai/charliepi/src/lib/object_detection/coco.names"
        with open(class_file, "rt") as f:
            self.class_names = f.read().rstrip("\n").split("\n")

        config_path = "/home/cai/charliepi/src/lib/object_detection/ssd_mobilenet_v3_large_coco_2020_01_14.pbtxt"
        weights_path = "/home/cai/charliepi/src/lib/object_detection/frozen_inference_graph.pb"

        self.net = cv2.dnn_DetectionModel(weights_path, config_path)
        self.net.setInputSize(320, 320)
        self.net.setInputScale(1.0 / 127.5)
        self.net.setInputMean((127.5, 127.5, 127.5))
        self.net.setInputSwapRB(True)

        self._picam2.configure(
            self._picam2.create_video_configuration(main={"size": (1280, 960)})
        )
        self._picam2.start_recording(JpegEncoder(), FileOutput(self._output))

    def stream_response(self):
        return self._stream(), "multipart/x-mixed-replace; boundary=frame"

    def stop(self):
        self._picam2.stop_recording()
        cv2.destroyAllWindows()

    def _stream(self):
        while True:
            with self._output._condition:
                self._output._condition.wait()

                frame = self._output._frame

                if self.object_detection_enabled:
                    # Process frame for object detection using OpenCV
                    f = cv2.imdecode(np.frombuffer(frame, np.uint8), cv2.IMREAD_COLOR)
                    result, _ = self.get_objects(
                        f, 0.45, 0.2, objects=["person", "cup"]
                    )
                    _, jpeg_frame = cv2.imencode(".jpeg", result)
                    jpeg_bytes = jpeg_frame.tobytes()
                    frame = jpeg_bytes

            yield (
                b"--frame\r\n"
                b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n"
            )

    # Function to get objects and draw bounding boxes
    def get_objects(self, img, thres, nms, draw=True, objects=[]):
        class_ids, confs, bbox = self.net.detect(
            img, confThreshold=thres, nmsThreshold=nms
        )
        if len(objects) == 0:
            objects = self.class_names
        object_info = []
        if len(class_ids) != 0:
            for class_id, confidence, box in zip(
                class_ids.flatten(), confs.flatten(), bbox
            ):
                class_name = self.class_names[class_id - 1]
                if class_name in objects:
                    object_info.append([box, class_name])
                    if draw:
                        cv2.rectangle(img, box, color=(0, 255, 0), thickness=2)
                        cv2.putText(
                            img,
                            self.class_names[class_id - 1].upper(),
                            (box[0] + 10, box[1] + 30),
                            cv2.FONT_HERSHEY_COMPLEX,
                            1,
                            (0, 255, 0),
                            2,
                        )
                        cv2.putText(
                            img,
                            str(round(confidence * 100, 2)),
                            (box[0] + 200, box[1] + 30),
                            cv2.FONT_HERSHEY_COMPLEX,
                            1,
                            (0, 255, 0),
                            2,
                        )

        return img, object_info

    class StreamingOutput(io.BufferedIOBase):
        def __init__(self):
            self._frame = None
            self._condition = threading.Condition()

        def write(self, buf):
            with self._condition:
                self._frame = buf
                self._condition.notify_all()
