
import numpy as np
import time
import threading 
import cv2
import picamera2
from libcamera import controls
import fractions
import io


class AcquisitionCamera(threading.Thread):

    def __init__(self, width=4056, height=3040):

        self.width = width
        self.height = height
        self.camera = picamera2.Picamera2()        
        self.capture_next_flag = False
        self.exposure_time = 50000

        threading.Thread.__init__(self)


    def capture_next(self):
        capture_next_flag = True
        

    def stop(self):
        self.do_run = False

    def set_exposure_time_ms(self,exp_time):
        self.exposure_time = np.int32(exp_time*1000)
        self.camera.set_controls({"ExposureTime": self.exposure_time})
        

    def start(self) :
        self.do_run = True
        
        print("Starting camera ")
        
        print(self.camera.camera_controls)
        print(self.camera.sensor_modes)
        
        self.camera.configure(self.camera.create_still_configuration(main={"format": 'XRGB8888', "size": (self.width,self.height) }))
        self.camera.set_controls({"ExposureTime": self.exposure_time, "AnalogueGain": 1.0, "AeEnable": False})
        self.camera.start()
        
        return threading.Thread.start(self)
        
        
    def run(self):

        self.do_run = True
        self.capture_next_flag = False
        while self.do_run:
            if self.capture_next_flag:                
                self.image_buffer = self.camera.capture_array()
                self.capture_next_flag = False

        self.camera.stop()