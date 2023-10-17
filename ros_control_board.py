import os
import sys
import time

from Rosmaster_Lib import Rosmaster
master = Rosmaster(com='COM5') if os.name == 'nt' else Rosmaster(com='/dev/ttyUSB0')
master.create_receive_threading()
last_time = 0
while True:
    print('====================================')
    print(master.get_gyroscope_data())
    print(master.get_magnetometer_data())
    print(master.get_accelerometer_data())
    print('====================================')
    now_time = time.time()
    print(now_time - last_time)
    last_time = now_time
    time.sleep(0.1)
sys.exit()
