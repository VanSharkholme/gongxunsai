import os
import sys
import time

from Rosmaster_Lib import Rosmaster
master = Rosmaster(com='COM5') if os.name == 'nt' else Rosmaster(com='/dev/ttyUSB0')
master.create_receive_threading()
while True:
    print('====================================')
    print(master.get_gyroscope_data())
    print(master.get_magnetometer_data())
    print(master.get_accelerometer_data())
    print('====================================')

    time.sleep(0.1)
sys.exit()
