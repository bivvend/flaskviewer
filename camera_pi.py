import io
import time
import picamera
from base_camera import BaseCamera
import cv2
import numpy as np


class Camera(BaseCamera):    
    @staticmethod
    def frames():
        with picamera.PiCamera() as camera:
            # let camera warm up
            time.sleep(2)
            stream = io.BytesIO()
            for _ in camera.capture_continuous(stream, 'jpeg',
                                                 use_video_port=True):
                # return current frame
                stream.seek(0)
                yield stream.read()

                # reset stream for next frame
                stream.seek(0)
                stream.truncate()

    def save_frame(self, filename):
        data = np.fromstring(Camera.stream.getvalue(), dtype=np.uint8)
        image = cv2.imdecode(data, 1)
        cv2.imwrite(filename, BaseCamera.frame)
        print('SAVE PI FRAME')
    
    
