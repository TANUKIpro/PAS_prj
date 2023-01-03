import serial
import time
import re

class Serial_communication:
    def __init__(self):
        self.ser = serial.Serial('/dev/ttyUSB0', 115200, timeout = 0.01)
        print("setting serial communication...")
        time.sleep(2)
        self.data = [0,0,0,0]

    def main(self):
        while True:
            for i in range(50):
                self.read_one()
                print(ser.data)
            self.clear_serial_buffer()
                
    def read_one(self):
        received = self.ser.read_until("k").decode('unicode-escape')
        #print(received, type(received))
        str_value = re.sub(r'\D',  '', received)
        if str_value is not "":
            data_kind = 3
            data_kind_str = received[0]
            if (data_kind_str == "a" ): data_kind = 0
            elif (data_kind_str == "b" ): data_kind = 1
            elif (data_kind_str == "c" ): data_kind = 2
            else: print("dataprotocol error")
            self.data[data_kind] = int(str_value)
            

    def clear_serial_buffer(self):
        self.ser.read_all()

if __name__ == '__main__':
    ser = Serial_communication()
    ser.main()