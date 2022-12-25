###############################################################
# This program is guaranteed to work with python3.9 or later. #
###############################################################

# defo
import os
import sys
import time
import subprocess
import socket
import xml.etree.ElementTree as ET

# local
import const
from const import Valve, Power, Julius

# RaspberryPi
import RPi.GPIO as GPIO


######## GPIO ########
def gpio_init():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(Power.CPS, GPIO.OUT)
    for __valve_gpio_l in const.VALVE_GPIO_LIST_L:
        GPIO.setup(__valve_gpio_l, GPIO.OUT)
    #for __valve_gpio_r in const.VALVE_GPIO_LIST_R:
    #    GPIO.setup(__valve_gpio_r, GPIO.OUT)

def valve_pressurization(target):
    GPIO.output(target.u, GPIO.LOW)
    GPIO.output(target.l, GPIO.LOW)

def valve_decompression(target):
    GPIO.output(target.u, GPIO.HIGH)
    GPIO.output(target.l, GPIO.HIGH)

def valve_keep(target):
    GPIO.output(target.u, GPIO.HIGH)
    GPIO.output(target.l, GPIO.LOW)


######## JULIUS ########
def julius_init():
    if subprocess.run("which julius", shell=True).returncode:
        print("julius is not find.")
        sys.exit()
    elif not os.path.exists(const.HOME + const.SR + Julius.Path.dictation):
        print(f"{Julius.Path.dictation} is not find.")
        sys.exit()
    elif not os.path.exists(const.HOME + const.SR + Julius.Path.grammar):
        print(f"{Julius.Path.grammar} is not find.")
        sys.exit()
    elif not os.path.exists(const.HOME + const.SR + Julius.Path.original_dict):
        print(f"{Julius.Path.original_dict} is not find.")
        sys.exit()
    else:
        pass

def julius_start():
    spell = f"julius -C {const.HOME + const.SR + Julius.Path.dictation}/hmm_mono.jconf -input mic -gram {const.HOME + const.SR + Julius.Path.original_dict}/command -module"
    spell_CompPrsObj = subprocess.run(spell, shell=True)
    if spell_CompPrsObj.returncode:
        print("failed start JULIUS")
        sys.exit()

def main():
    # 電磁弁の初期化
    gpio_init()

    # Julius関連のファイル整合性チェック
    julius_init()

    # Juliusの起動
    julius_start()

    # Juliusの接続
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((Julius.Con.host, Julius.Con.port))

    # 音声待ち
    try:
        data = ''
        while True:
            if '</RECOGOUT>\n.' in data:
                root = ET.fromstring('<?xml version="1.0"?>\n' + data[data.find('<RECOGOUT>'):].replace('\n.', ''))
                for whypo in root.findall('./SHYPO/WHYPO'):
                    command = whypo.get('WORD')
                    score = float(whypo.get('CM'))
                    print(command + ':' + str(score))
                    if (key_Rise[0] in command) and score >= Julius.Param.word_threshold:
                        print('rise')
                        valve_gain(valve_01, valve_02)
                    elif (key_Fall[0] in command) and score >= Julius.Param.word_threshold:
                        print('fall')
                        valve_reduction(valve_01, valve_02)
                    elif (key_Stop[0] in command) and score >= Julius.Param.word_threshold:
                        print('stop')
                        valve_stop(valve_01, valve_02)
                data = ''
            else:
                data = data + client.recv(1024).decode('utf-8')

    except KeyboardInterrupt:
        client.close()
