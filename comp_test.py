import time
import RPi.GPIO as GPIO

pin_num = 18

GPIO.setmode(GPIO.BCM)
GPIO.setup(pin_num, GPIO.OUT)

GPIO.output(pin_num, 1)

try:
    while True:
        #GPIO.output(pin_num, 1)
        pass
except KeyboardInterrupt:
    GPIO.output(pin_num, 0)
    GPIO.cleanup(pin_num)

    GPIO.setup(pin_num, GPIO.OUT)
