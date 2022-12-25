import sys, time
import RPi.GPIO as GPIO
import const
from const import Valve, Power

def gpio_init():
    GPIO.setmode(GPIO.BCM)

    # 任意のGPIOを出力モードへ
    GPIO.setup(Power.CPS, GPIO.OUT)
    #for __valve_gpio_r in const.VALVE_GPIO_LIST_R:
    #    GPIO.setup(__valve_gpio_r, GPIO.OUT)

    for __valve_gpio_l in const.VALVE_GPIO_LIST_L:
        GPIO.setup(__valve_gpio_l, GPIO.OUT)


def valve_pressurization(target):
    GPIO.output(target.u, GPIO.LOW)
    GPIO.output(target.l, GPIO.LOW)

def valve_decompression(target):
    GPIO.output(target.u, GPIO.HIGH)
    GPIO.output(target.l, GPIO.HIGH)

def valve_keep(target):
    GPIO.output(target.u, GPIO.HIGH)
    GPIO.output(target.l, GPIO.LOW)

if __name__=='__main__':
    try:
        gpio_init()

        valve_decompression(Valve.Right.B)
        valve_decompression(Valve.Right.C)

        tgt = Valve.Right.A

        while True:
            print('stop')
            valve_keep(tgt)
            time.sleep(2)
            
            print('gain')
            valve_pressurization(tgt)
            time.sleep(2)
            
            print('reduction')
            valve_decompression(tgt)
            time.sleep(2)
            
    except KeyboardInterrupt:
        GPIO.cleanup()

