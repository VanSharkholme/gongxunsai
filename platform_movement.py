import sys
import time

from Rosmaster_Lib import Rosmaster


class Platform:
    def __init__(self):
        self.master = Rosmaster(com='COM5')
        self.master.create_receive_threading()

    def straight_pid_distance(self, p, i, d):

        self.master.set_car_motion(0.15, 0, 0)
        # time.sleep(50)
        # self.master.set_car_motion(0, 0, 0)
        pass

    def stop(self):
        self.master.set_car_motion(0, 0, 0)

    def odometry(self):
        a1, a2, a3, a4 = self.master.get_motor_encoder()
        print('\r', str(a1), str(a2), str(a3), str(a4), end="")


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
