import cv2
import time
import numpy as np
from base_camera import BaseCamera


class Camera(BaseCamera):
    video_source = 0
    
    @staticmethod
    def set_video_source(source):
        Camera.video_source = source
	
    @staticmethod
    def frames():
        camera = cv2.VideoCapture(Camera.video_source,cv2.CAP_V4L)
        camera.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        camera.set(cv2.CAP_PROP_AUTOFOCUS, 0)
        if not camera.isOpened():
            raise RuntimeError('Could not start camera.')
        ok_flag = True
        last_focus = 0
        while ok_flag:
            time.sleep(0.0)
            if last_focus != BaseCamera.focus_value:
                print("Here")
                camera.set(cv2.CAP_PROP_FOCUS, BaseCamera.focus_value)
                last_focus = BaseCamera.focus_value
            ok_flag, img = camera.read()
            if not BaseCamera.running:
                if BaseCamera.in_cycle:
                    time.sleep(0.2)
                    print("Saving image to buffer")                    
                    img_num = len(BaseCamera.image_buffer_list)
                    print(BaseCamera.focus_value)                    
                    step_num = str(int(BaseCamera.focus_value)*100)
                    BaseCamera.image_buffer_list.append((str(img_num) + "_" + step_num + ".jpg", img))
                    print("{} images stored".format(len(BaseCamera.image_buffer_list)))
                else:
                    print("Saving image in {}".format(BaseCamera.file_path))
                    cv2.imwrite(BaseCamera.file_path, img)
            yield cv2.imencode('.jpg', img)[1].tobytes()
    @staticmethod
    def save_frame(file_name):
        return
