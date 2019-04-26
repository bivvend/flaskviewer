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
            time.sleep(0.1)
            stream = io.BytesIO()
            print("Camera warm up done")
            for _ in camera.capture_continuous(stream, 'jpeg',
                                                 use_video_port=True):
                # return current frame
                stream.seek(0)
                #print(BaseCamera.running)
                if not BaseCamera.running:
                    if BaseCamera.in_cycle:
                        print("Saving image to buffer".format(BaseCamera.file_path))
                        data = np.fromstring(stream.getvalue(), dtype = np.uint8)
                        img = cv2.imdecode(data, 1)
                        BaseCamera.image_buffer_list.append(img)
                    else:
                        print("Saving image in {}".format(BaseCamera.file_path))
                        data = np.fromstring(stream.getvalue(), dtype = np.uint8)
                        img = cv2.imdecode(data, 1)
                        cv2.imwrite(BaseCamera.file_path, img)
                if BaseCamera.in_cycle:
                    print("{} images stored".format(len(BaseCamera.image_buffer_list)))
                yield stream.read()
                # reset stream for next frame
                stream.seek(0)
                stream.truncate()

    
    
