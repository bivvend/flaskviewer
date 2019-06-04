#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  stepper_controller.py
#  

import sys
import RPi.GPIO as GPIO
import time

class StepperController():
    def __init__(self, pin_list_in = [29,31,33,35]):
        GPIO.setmode(GPIO.BOARD)
        self.control_pins = pin_list_in
        for pin in self.control_pins:
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, 0)
        self.halfstep_seq = [
          [1,0,0,0],
          [1,1,0,0],
          [0,1,0,0],
          [0,1,1,0],
          [0,0,1,0],
          [0,0,1,1],
          [0,0,0,1],
          [1,0,0,1]
        ]        
        
    def set_freq(self, freq_in):
        self.freq = freq_in
        
    def start(self):
        for i in range(512):
            for halfstep in range(8):
                for pin in range(4):
                    GPIO.output(self.control_pins[pin], self.halfstep_seq[halfstep][pin])
                    time.sleep(0.001)
        GPIO.cleanup()
    
    def stop(self):
        pass
        
if __name__ == '__main__':
    s = StepperController()
    s.start()     
    
