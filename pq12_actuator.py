#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  pq12actuator.py
#  

import sys
import pigpio
import time

class PQ12actuator():
    
    def __init__(self, pin_in = 18, freq_in = 1000, start_duty = 0):
        self.pin_number = pin_in
        self.freq = freq_in
        if(start_duty > 0.95):
            start_duty = 0.95
        if(start_duty < 0.01):
            start_duty = 0.0
        self.duty = start_duty 
        self.duty_max = 1000000.0
        self.pi = None
        
    def set_pin(self, pin_in):
        self.pin_number = pin_in
        
    def set_freq(self, freq_in):
        self.freq = freq_in
        
    def set_duty(self, duty):
        if(duty > 0.95):
            duty = 0.95
        if(duty < 0.01):
            duty = 0.0
        self.duty = duty
        if self.pi is not None:
            self.pi.hardware_PWM(self.pin_number, self.freq, int(self.duty_max * self.duty))
        
        
    def start(self):
        if self.pi is None:
            self.pi = pigpio.pi()
            self.pi.hardware_PWM(self.pin_number, self.freq, int(self.duty_max * self.duty))
        else:
            print("pigpio is already running.")
    
    def stop(self):
        if self.pi is not None:
            self.pi.hardware_PWM(self.pin_number, 0, 0)
        else:
            print("pigpio is not running.")
        
        
    
