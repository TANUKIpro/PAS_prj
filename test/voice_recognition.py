import socket
import xml.etree.ElementTree as ET

host = '127.0.0.1'
port = 10500

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((host, port))

def get_root(data):
    try:
        root = ET.fromstring('<?xml version="1.0"?>\n' + data[data.find('<RECOGOUT>'):].replace('\n.', ''))
    except:
        root = None
    return root

try:
    data = ''
    while True:
        if '</RECOGOUT>\n.' in data:
            root = get_root(data)
            if root is None:
                continue
            for whypo in root.findall('./SHYPO/WHYPO'):
                command = whypo.get('WORD')
                score = float(whypo.get('CM'))
                print(command + ':' + str(score))
            data = ''
        else:
            data = data + client.recv(1024).decode('utf-8')#バイト列を文字列に変更してから連結

except KeyboardInterrupt:
    client.close()
