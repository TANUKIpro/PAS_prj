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

# 加圧
def valve_pressurization(target):
    GPIO.output(target.u, GPIO.LOW)
    GPIO.output(target.l, GPIO.LOW)

# 減圧
def valve_decompression(target):
    GPIO.output(target.u, GPIO.HIGH)
    GPIO.output(target.l, GPIO.HIGH)

# 維持
def valve_keep(target):
    GPIO.output(target.u, GPIO.HIGH)
    GPIO.output(target.l, GPIO.LOW)


######## JULIUS ########
def julius_init():
    if subprocess.run("which julius", shell=True).returncode:
        print("julius is not find.")
        sys.exit()
    elif not os.path.exists(Julius.Path.dictation):
        print(f"{Julius.Path.dictation} is not find.")
        sys.exit()
    elif not os.path.exists(Julius.Path.grammar):
        print(f"{Julius.Path.grammar} is not find.")
        sys.exit()
    elif not all([cmd for cmd in const.Julius.Path.orgn_dict if os.path.exists(cmd)]):
        print(f"{Julius.Path.orgn_dict} is not find.")
        sys.exit()
    else:
        pass

def julius_start():
    #spell = "julius -C ~/dictation-kit/am-gmm.jconf -input mic -gram ~/PAS_prj/original_3/command -nostrip -module"
    #spell = f"exec julius -C {Julius.Path.grammar}/hmm_mono.jconf -input mic -gram {const.HOME+const.WS+Julius.Path.original_dict}/command -module"
    spell = f"julius -C {Julius.Path.grammar} -input mic -gram {const.Julius.Path.orgn_dict[0]},{const.Julius.Path.orgn_dict[1]},{const.Julius.Path.orgn_dict[2]} -module"
    spell_CompPrsObj = subprocess.Popen(spell, shell=True, stdout=subprocess.DEVNULL)
    if spell_CompPrsObj.returncode:
        print("failed start JULIUS")
        sys.exit()
    else:
        return spell_CompPrsObj

def word_inspection(target, recog_word_list, score_list, th=Julius.Param.word_threshold) -> bool:
    matched_word = list(set(target) & set(recog_word_list))
    is_understand = bool(matched_word)
    if is_understand:
        score_idx = recog_word_list.index(matched_word[0])
        is_satisfy = score_list[score_idx] >= th
        return is_understand and is_satisfy
    else:
        return False

def get_root(data):
    try:
        root = ET.fromstring('<?xml version="1.0"?>\n' + data[data.find('<RECOGOUT>'):].replace('\n.', ''))
    except:
        root = None
    return root

def main():
    # 電磁弁の初期化
    gpio_init()

    # Julius関連のファイル整合性チェック
    julius_init()

    # Juliusの起動
    cmd_obj = julius_start()

    # Juliusの接続
    time.sleep(0.5)
    try:
        julius_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        julius_client.connect((Julius.Con.host, Julius.Con.port))
        print("success connection.")
    except:
        print("connection error.")

    # 音声認識と対応する動作の実行
    try:
        julius_xml_data = ''
        while True:
            if '</RECOGOUT>\n.' in julius_xml_data:
                root = get_root(julius_xml_data)
                if root is None:
                    julius_xml_data = ''
                    continue
                else:
                    hex_raw = root.findall('./SHYPO/WHYPO')
                    recog_words  = [raw.get('WORD') for raw in hex_raw][1:-1] # <-- pop header and footer
                    recog_scores = [float(raw.get('CM')) for raw in hex_raw][1:-1] # <-- pop header and footer

                    print(recog_words, recog_scores)
                    # 緊急停止
                    if word_inspection(Julius.OrderSet.Eme_Stop, recog_words, recog_scores, th=0.5):
                        print("緊急停止")
                        for __valve_gpio_l in const.VALVE_GPIO_LIST_L:
                            GPIO.output(__valve_gpio_l, GPIO.HIGH)
                        for __valve_gpio_r in const.VALVE_GPIO_LIST_R:
                            GPIO.output(__valve_gpio_r, GPIO.HIGH)

                    # コンプレッサー
                    elif word_inspection(Julius.OrderSet.CPS, recog_words, recog_scores):
                        print("コンプレッサー")
                        recog_words.pop(0)
                        recog_scores.pop(0)
                        if word_inspection(Julius.OrderSet.On, recog_words, recog_scores, th=0.6):
                            print("On")
                            GPIO.output(Power.CPS, GPIO.HIGH)
                        elif word_inspection(Julius.OrderSet.Off, recog_words, recog_scores, th=0.6):
                            print("Off")
                            GPIO.output(Power.CPS, GPIO.LOW)
                    
                    # TODO:ここに左右判定
                    # 上腕, 肩 (TYPE : A)
                    elif word_inspection(Julius.OrderSet.UpperArm, recog_words, recog_scores):
                        print("上腕, 肩")
                        recog_words.pop(0)
                        recog_scores.pop(0)
                        # 屈曲
                        if word_inspection(Julius.OrderSet.Rise, recog_words, recog_scores):
                            print("屈曲")
                            valve_pressurization(Valve.Left.A)
                        # 伸展
                        elif word_inspection(Julius.OrderSet.Fall, recog_words, recog_scores):
                            print("伸展")
                            valve_decompression(Valve.Left.A)
                        # 停止
                        elif word_inspection(Julius.OrderSet.Stop, recog_words, recog_scores):
                            print("停止")
                            valve_keep(Valve.Left.A)

                    # 腕, 肘 (TYPE : B, C)
                    elif word_inspection(Julius.OrderSet.LowerArm, recog_words, recog_scores):
                        print("肘")
                        recog_words.pop(0)
                        recog_scores.pop(0)
                        # 屈曲
                        if word_inspection(Julius.OrderSet.Rise, recog_words, recog_scores):
                            print("屈曲")
                            valve_pressurization(Valve.Left.B)
                            valve_decompression(Valve.Left.C)
                        # 伸展
                        elif word_inspection(Julius.OrderSet.Fall, recog_words, recog_scores):
                            print("伸展")
                            valve_decompression(Valve.Left.B)
                            valve_pressurization(Valve.Left.C)
                        # 停止
                        elif word_inspection(Julius.OrderSet.Stop, recog_words, recog_scores):
                            print("停止")
                            valve_keep(Valve.Left.B)
                            valve_keep(Valve.Left.C)

                julius_xml_data = ''
            else:
                julius_xml_data = julius_xml_data + julius_client.recv(1024).decode('utf-8')

    except KeyboardInterrupt:
        julius_client.send("DIE".encode("utf-8"))
        julius_client.close()
        GPIO.cleanup()

if __name__=="__main__":
    main()
