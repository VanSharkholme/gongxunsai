import os
import sys
import serial


def send_serial(message):
    try:
        portx = "COM4" if os.name == 'nt' else "/dev/screen"
        bps = 115200
        timex = 5
        ser = serial.Serial(portx, bps, timeout=timex)
        print(ser)
        # message = "1"
        # print()
        result = ser.write(('t0.txt="' + message + '"').encode('utf-8') + bytes.fromhex('ff ff ff'))
        # ser.write(bytes.fromhex('ff ff ff'))
        data = ser.readline()
        print(data)
        ser.close()
    except Exception as e:
        print(e)


if __name__ == '__main__':
    send_serial('123+\r\n321')
