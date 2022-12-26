###############################################################
# This program is guaranteed to work with python3.9 or later. #
###############################################################

# built-in
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
    for __valve_gpio_r in const.VALVE_GPIO_LIST_R:
        GPIO.setup(__valve_gpio_r, GPIO.OUT)

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
    elif not os.path.exists(const.HOME + Julius.Path.dictation):
        print(f"{Julius.Path.dictation} is not find.")
        sys.exit()
    elif not os.path.exists(const.HOME + Julius.Path.grammar):
        print(f"{Julius.Path.grammar} is not find.")
        sys.exit()
    elif not os.path.exists(const.HOME + const.WS + Julius.Path.original_dict):
        print(f"{Julius.Path.original_dict} is not find.")
        sys.exit()
    else:
        pass

def julius_start():
    spell = f"julius -C {const.HOME+Julius.Path.grammar}/hmm_mono.jconf -input mic -gram {const.HOME+const.WS+Julius.Path.original_dict}/command -module"
    spell_CompPrsObj = subprocess.run(spell, shell=True)
    if spell_CompPrsObj.returncode:
        print("failed start JULIUS")
        sys.exit()

def word_inspection(recog_word, target, score, th=Julius.Param.word_threshold) -> bool:
    is_understand = bool(list(set(target) & set(recog_word)))
    is_satisfy = score >= th
    return is_understand and is_satisfy

def main():
    # 電磁弁の初期化
    gpio_init()

    # Julius関連のファイル整合性チェック
    julius_init()

    # Juliusの起動
    julius_start()

    # Juliusの接続
    julius_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    julius_client.connect((Julius.Con.host, Julius.Con.port))

    # 音声認識と対応する動作の実行
    try:
        julius_xml_data = ''
        while True:
            if '</RECOGOUT>\n.' in julius_xml_data:
                root = ET.fromstring('<?xml version="1.0"?>\n' + julius_xml_data[julius_xml_data.find('<RECOGOUT>'):].replace('\n.', ''))
                for whypo in root.findall('./SHYPO/WHYPO'):
                    command = whypo.get('WORD')
                    score = float(whypo.get('CM'))
                    # 緊急停止
                    if word_inspection(command, Julius.OrderSet.Ema_Stop, score, th=0.5):
                        for __valve_gpio_l in const.VALVE_GPIO_LIST_L:
                            GPIO.output(__valve_gpio_l, GPIO.HIGH)
                        for __valve_gpio_r in const.VALVE_GPIO_LIST_R:
                            GPIO.output(__valve_gpio_r, GPIO.HIGH)
                    
                    # TODO:ここに左右判定
                    # 腕、上腕 (TYPE : A)
                    elif word_inspection(command, Julius.OrderSet.UpperArm, score):
                        # 屈曲
                        if word_inspection(command, Julius.OrderSet.Rise, score):
                            valve_pressurization(Valve.Left.A)
                        # 伸展
                        elif word_inspection(command, Julius.OrderSet.Fall, score):
                            valve_decompression(Valve.Left.A)
                        # 停止
                        elif word_inspection(command, Julius.OrderSet.Stop, score):
                            valve_keep(Valve.Left.A)

                    # 肘 (TYPE : B, C)
                    elif word_inspection(command, Julius.OrderSet.LowerArm, score):
                        # 屈曲
                        if word_inspection(command, Julius.OrderSet.Rise, score):
                            valve_pressurization(Valve.Left.B)
                            valve_decompression(Valve.Left.C)
                        # 伸展
                        elif word_inspection(command, Julius.OrderSet.Fall, score):
                            valve_decompression(Valve.Left.B)
                            valve_pressurization(Valve.Left.C)
                        # 停止
                        elif word_inspection(command, Julius.OrderSet.Stop, score):
                            valve_keep(Valve.Left.B)
                            valve_keep(Valve.Left.C)

                    # コンプレッサー
                    elif word_inspection(command, Julius.OrderSet.CPS, score):
                        if word_inspection(command, Julius.OrderSet.On, score):
                            GPIO.output(Power.CPS, GPIO.HIGH)
                        elif word_inspection(command, Julius.OrderSet.Off, score):
                            GPIO.output(Power.CPS, GPIO.LOW)

                julius_xml_data = ''
            else:
                julius_xml_data = julius_xml_data + julius_client.recv(1024).decode('utf-8')

    except KeyboardInterrupt:
        julius_client.close()
        GPIO.cleanup()

if __name__=="__main__":
    main()
