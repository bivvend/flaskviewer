#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  stepper_controller.py
#  

import sys
import RPi.GPIO as GPIO
import time
import threading

class StepperController():
    def __init__(self, pin_list_in = [29,31,33,35]):
        GPIO.setmode(GPIO.BOARD)
        self.control_pins = pin_list_in
        self.running = False
        self.thread = None
        self.forward = True
        self.step_count = 0
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
        
        self.rev_halfstep_seq = list(reversed(self.halfstep_seq))  
        
    def set_freq(self, freq_in):
        self.freq = freq_in
    
    def step_thead(self):
        while self.running:
            self.step(1)
        
    
    def step(self, number = 1):
        time.sleep(0.001)
        for step_num in range(number):
            for halfstep in range(8):
                for pin in range(4):
                    if self.forward:
                        GPIO.output(self.control_pins[pin], self.halfstep_seq[halfstep][pin])
                    else:
                        GPIO.output(self.control_pins[pin], self.rev_halfstep_seq[halfstep][pin])
                    time.sleep(0.001)
            if self.forward:
                self.step_count +=1
            else:
                self.step_count -= 1
            print(self.step_count)
            
    def start(self):
        self.running = True
        if self.thread is None:
            self.thread = threading.Thread(target = self.step_thead)
            self.thread.start()
        
    def set_direction(self, forward = True):
        if forward:
            self.forward = True
        else:
            self.forward = False
            
    def stop(self):
        self.running = False
        self.thread = None
        
    def make_step(self, number = 1, forward = True):
        if self.thread is None:
            self.set_direction(forward)
            if self.thread is None:
                self.step(number)                
        self.reset_pins()
        return self.get_count()
    
    def reset_pins(self):
        for pin in range(4):
            GPIO.output(self.control_pins[pin], 0)
        
    def get_count(self):
        return self.step_count
        
    def reset_count(self):
        self.step_count = 0
        print("Zeroed step count")
        
    def move_to_count(self, target):
        if self.thread is None:
            moving = True
            while moving:
                if target > self.get_count():
                    self.make_step(1, True)
                if target < self.get_count():
                    self.make_step(1, False)
                if target == self.get_count():
                    break
            print("Found count target of {0}".format(target))
        
    def home(self):
        if self.thread is None:
            self.move_to_count(0)
            self.reset_count()
            
    def clean_up(self):
        s.stop()
        GPIO.cleanup()
        
if __name__ == '__main__':
    try:
        s = StepperController()
        #s.start()
        #time.sleep(3)
        #s.set_direction(False)
        #time.sleep(3)
        #s.stop()
        #time.sleep(1)
        #s.make_step(1, False)
        s.move_to_count(100)
        s.home()
        GPIO.cleanup()
    except Exception as e:
        print(e)
        s.stop()
        GPIO.cleanup()

    
