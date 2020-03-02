import cv2
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
        if not camera.isOpened():
            raise RuntimeError('Could not start camera.')
        ok_flag = True
        while ok_flag:
            ok_flag, img = camera.read()
            if not BaseCamera.running:
                if BaseCamera.in_cycle:
                    print("Saving image to buffer")                    
                    img_num = len(BaseCamera.image_buffer_list)
                    step_num = str(BaseCamera.stepper.get_count())
                    BaseCamera.image_buffer_list.append((str(img_num) + "_" + step_num + ".jpg", img))
                else:
                    print("Saving image in {}".format(BaseCamera.file_path))
                    cv2.imwrite(BaseCamera.file_path, img)
                if BaseCamera.in_cycle:
                    print("{} images stored".format(len(BaseCamera.image_buffer_list)))
            yield cv2.imencode('.jpg', img)[1].tobytes()
    @staticmethod
    def save_frame(file_name):
        return
