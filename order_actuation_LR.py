import time
import socket
import xml.etree.ElementTree as ET
import RPi.GPIO as GPIO

host = '127.0.0.1'
port = 10500

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((host, port))

pin_l1 = 40
pin_l2 = 38
pin_l3 = 36
pin_l4 = 29
pin_l5 = 31
pin_l6 = 33

pin_r1 = 16
pin_r2 = 18
pin_r3 = 15
pin_r4 = 7
pin_r5 = 11
pin_r6 = 13


GPIO.setmode(GPIO.BCM)
GPIO.setup(valve_01, GPIO.OUT)
GPIO.setup(valve_02, GPIO.OUT)

key_UpperArm = ['腕', '上腕']
key_LowerArm = ['肘']
key_Rise = ['挙げ']
key_Fall = ['下げ']
key_Stop = ['停止']

def valve_stop(v_in, v_out):
    GPIO.output(v_in, 1)
    GPIO.output(v_out, 0)

def valve_gain(v_in, v_out):
    GPIO.output(v_in, 0)
    GPIO.output(v_out, 0)

def valve_reduction(v_in, v_out):
    GPIO.output(v_in, 1)
    GPIO.output(v_out, 1)

word_th = 0.95

try:
    data = ''
    while True:
        if '</RECOGOUT>\n.' in data:
            root = ET.fromstring('<?xml version="1.0"?>\n' + data[data.find('<RECOGOUT>'):].replace('\n.', ''))
            for whypo in root.findall('./SHYPO/WHYPO'):
                command = whypo.get('WORD')
                score = float(whypo.get('CM'))
                #print(command + ':' + str(score))
                if (key_Rise[0] in command) and score >= word_th:
                    print('rise')
                    valve_gain(valve_01, valve_02)
                elif (key_Fall[0] in command) and score >= word_th:
                    print('fall')
                    valve_reduction(valve_01, valve_02)
                elif (key_Stop[0] in command) and score >= word_th:
                    print('stop')
                    valve_stop(valve_01, valve_02)
            data = ''
        else:
            data = data + client.recv(1024).decode('utf-8')

except KeyboardInterrupt:
    client.close()