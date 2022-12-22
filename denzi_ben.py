import time
import RPi.GPIO as GPIO

cpr_PW = 18
cprL_A_u = 13
cprL_A_l = 6
cprL_B_u = 5
cprL_B_l = 16
cprL_C_u = 20
cprL_C_l = 21

GPIO.setmode(GPIO.BCM)

GPIO.setup(cpr_PW, GPIO.OUT)
GPIO.setup(cprL_A_u, GPIO.OUT)
GPIO.setup(cprL_A_l, GPIO.OUT)

def valve_stop(v_in, v_out):
    GPIO.output(v_in, 1)
    GPIO.output(v_out, 0)

def valve_gain(v_in, v_out):
    GPIO.output(v_in, 0)
    GPIO.output(v_out, 0)

def valve_reduction(v_in, v_out):
    GPIO.output(v_in, 1)
    GPIO.output(v_out, 1)


try:
    while True:
        print('stop')
        valve_stop(cprL_A_u, cprL_A_l)
        time.sleep(2)
        
        print('gain')
        valve_gain(cprL_A_u, cprL_A_l)
        time.sleep(2)
        
        print('reduction')
        valve_reduction(cprL_A_u, cprL_A_l)
        time.sleep(2)
        
except KeyboardInterrupt:
    GPIO.cleanup()

