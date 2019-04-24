#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  pq12_hw_pwm.py
import sys
import pigpio
import time

if __name__ == '__main__':
    print("Hello") 
    pi = pigpio.pi()
    try:
        while True:
            pi.hardware_PWM(18, 1000, 100000)
            time.sleep(10)
            pi.hardware_PWM(18, 1000, 800000)
            time.sleep(10)
            pi.hardware_PWM(18, 1000, 100000)
            time.sleep(10)
            pi.hardware_PWM(18, 1000, 800000)
            time.sleep(10)
    except KeyboardInterrupt:
        pi.hardware_PWM(18, 0, 0)
        
