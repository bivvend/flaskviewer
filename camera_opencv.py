import cv2
import numpy as np
from base_camera import BaseCamera


class Camera(BaseCamera):
    video_source = 0
    

    def set_video_source(self, source):
        Camera.video_source = source

    def frames(self):
        camera = cv2.VideoCapture(Camera.video_source)
        if not camera.isOpened():
            raise RuntimeError('Could not start camera.')

        while True:
            # read current frame
            _, img = camera.read()

            # encode as a jpeg image and return it
            yield cv2.imencode('.jpg', img)[1].tobytes()

    def save_frame(self, file_name):
        return
