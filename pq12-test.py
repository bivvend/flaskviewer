import RPi.GPIO as GPIO     # Importing RPi library to use the GPIO pins
from time import sleep      # Importing sleep from time library to add delay in code
servo_pin = 18     # Initializing the GPIO 21 for servo motor
GPIO.setmode(GPIO.BCM)          # We are using the BCM pin numbering
GPIO.setup(servo_pin, GPIO.OUT)     # Declaring GPIO  18 as output pin
p = GPIO.PWM(servo_pin, 1000)     # Created PWM channel at 1000 Hz frequency
try:
    p.start(50) 
    while True:
        sleep(1)
# If Keyborad Interrupt (CTRL+C) is pressed
except KeyboardInterrupt:
    p.stop()
    pass   # Go to next line
GPIO.cleanup()              # Make all GPIO pins LOW
