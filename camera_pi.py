import io
import time
import picamera
from base_camera import BaseCamera
import cv2
import numpy as np


class Camera(BaseCamera):

    @staticmethod
    def frames():
        with picamera.PiCamera(resolution = (1000, 1000), framerate = 20) as camera:
        #with picamera.PiCamera(resolution = (2560, 1440), framerate = 2) as camera:
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
                        print("Saving image to buffer")
                        data = np.fromstring(stream.getvalue(), dtype = np.uint8)
                        img = cv2.imdecode(data, 1)
                        img_num = len(BaseCamera.image_buffer_list)
                        step_num = str(BaseCamera.stepper.get_count())
                        BaseCamera.image_buffer_list.append((str(img_num) + "_" + step_num + ".jpg", img))
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

    
    
