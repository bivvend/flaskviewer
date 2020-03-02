import time
import cv2
import numpy as np
import threading
import os

try:
    from greenlet import getcurrent as get_ident
except ImportError:
    try:
        from thread import get_ident
    except ImportError:
        from _thread import get_ident


class CameraEvent(object):
    """An Event-like class that signals all active clients when a new frame is
    available.
    """
    def __init__(self):
        self.events = {}

    def wait(self):
        """Invoked from each client's thread to wait for the next frame."""
        ident = get_ident()
        if ident not in self.events:
            # this is a new client
            # add an entry for it in the self.events dict
            # each entry has two elements, a threading.Event() and a timestamp
            self.events[ident] = [threading.Event(), time.time()]
        return self.events[ident][0].wait()

    def set(self):
        """Invoked by the camera thread when a new frame is available."""
        now = time.time()
        remove = None
        for ident, event in self.events.items():
            if not event[0].isSet():
                # if this client's event is not set, then set it
                # also update the last set timestamp to now
                event[0].set()
                event[1] = now
            else:
                # if the client's event is already set, it means the client
                # did not process a previous frame
                # if the event stays set for more than 5 seconds, then assume
                # the client is gone and remove it
                if now - event[1] > 5:
                    remove = ident
        if remove:
            del self.events[remove]

    def clear(self):
        """Invoked from each client's thread after a frame was processed."""
        self.events[get_ident()][0].clear()


class BaseCamera(object):
    thread = None  # background thread that reads frames from camera
    frame = None  # current frame is stored here by background thread
    last_access = 0  # time of last client access to the camera
    event = CameraEvent()
    running = False # Used to toggle saving during grabbing
    in_cycle = False # Used to toggle if saving should make new images
    file_path = "output.jpg" # default
    image_buffer_list = []  #tuples of filename, image data
    stepper = None
    focus_value = 0
    def __init__(self):
        """Start the background camera thread if it isn't running yet."""
        if BaseCamera.thread is None:
            BaseCamera.last_access = time.time()

            # start background frame thread
            BaseCamera.thread = threading.Thread(target=self._thread)
            BaseCamera.thread.start()
            
            # wait until frames are available
            while self.get_frame() is None:
                time.sleep(1)
            BaseCamera.running = True

    def set_focal_position(self, focus):
        """Sets the focus value"""
        print("Setting focus to {0}".format(focus))
        BaseCamera.focus_value = focus
        
    def get_focal_position(self):
        """Gets the focus value"""
        return BaseCamera.focus_value
        
    def step_focal_position(self, step):
        """Sets the focus value"""
        print("Moving focus  by {0}".format(step))
        BaseCamera.focus_value += step
                  
    def set_running_state(self, state_in, in_cycle_in):
        """Sets the state True is grabbing without saving, False = saving"""
        print("Setting")
        BaseCamera.running = state_in
        BaseCamera.in_cycle = in_cycle_in
    
    def clear_buffers(self):
        '''Clears the image buffers.'''        
        BaseCamera.image_buffer_list = []
    
    def load_images_to_buffers(self, directory):
        BaseCamera.image_buffer_list = []
        for file in os.listdir(directory):
            if ".jpg" in file and "best" not in file:
                im = cv2.imread(os.path.join(directory, file))
                BaseCamera.image_buffer_list.append((file, im))
        print("{0} Images loaded".format(len(BaseCamera.image_buffer_list)))
    
    def save_buffers(self, directory, delete_files):
        '''Saves the buffers to file. Warning will delete any images in that directory first.'''
        if delete_files:
            for file in os.listdir(directory):
                if ".jpg" in file:
                    os.remove(os.path.join(directory, file))
            for i, im in BaseCamera.image_buffer_list:
                print("Saving {}".format(i))
                cv2.imwrite(os.path.join(directory, i), im)
        
    def get_running_state(self):
        """Returns the state true is grabbing without saving, False = saving"""
        return BaseCamera.running
            
    def get_frame(self):
        """Return the current camera frame."""
        BaseCamera.last_access = time.time()

        # wait for a signal from the camera thread
        BaseCamera.event.wait()
        BaseCamera.event.clear()

        return BaseCamera.frame   
        
    def set_save_location(self, file_path_in):
        """Sets the file path for saving"""
        BaseCamera.file_path = file_path_in

    @staticmethod
    def frames():
        """"Generator that returns frames from the camera."""
        raise RuntimeError('Must be implemented by subclasses.')

    @classmethod
    def _thread(cls):
        """Camera background thread."""
        print('Starting camera thread.')
        frames_iterator = cls.frames()
        for frame in frames_iterator:
            BaseCamera.frame = frame
            BaseCamera.event.set()  # send signal to clients
            time.sleep(0)

            # if there hasn't been any clients asking for frames in
            # the last 10 seconds then stop the thread
            # if time.time() - BaseCamera.last_access > 10:
            #     frames_iterator.close()
            #     print('Stopping camera thread due to inactivity.')
            #     break
        BaseCamera.thread = None
