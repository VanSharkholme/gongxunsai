import sys
import time
from os import name as os_name
import threading
from Rosmaster_Lib import Rosmaster


class Platform:
    def __init__(self):
        if os_name == 'nt':
            self.master = Rosmaster(com='COM5')
        else:
            self.master = Rosmaster(com='/dev/ttyUSB0')

        self.master.create_receive_threading()
        self.condition = threading.Condition()
        self.kp = 1
        self.ki = 0
        self.kd = 0
        # self.condition.
    # def motor

    def get_cur_position(self):
        return 1, 2
        pass

    def pid_velocity(self, err):
        out_put_vel = self.kp * err +

    def straight_pid_distance(self, x, y):
        cur_x, cur_y = self.get_cur_position()
        ex = x - cur_x
        ey = y - cur_y
        vx = self.pid_velocity(ex)
        vy = self.pid_velocity(ey)
        self.master.set_car_motion(0.15, 0, 0)
        # time.sleep(50)
        # self.master.set_car_motion(0, 0, 0)
        print(time.time())
        pass

    def stop(self):
        self.master.set_car_motion(0, 0, 0)

    def odometry(self):
        a1, a2, a3, a4 = self.master.get_motor_encoder()
        vx, vy, vz = self.master.get_motion_data()
        print('\r', str(a1), str(a2), str(a3), str(a4), end="")
        print(vx, vy, vz, end='')


if __name__ == '__main__':
    p = Platform()
    p.master.create_receive_threading()
    p.straight_pid_distance(0, 0, 0)
    try:
        while True:
            p.odometry()
    finally:
        p.stop()
        sys.exit()
    pass
