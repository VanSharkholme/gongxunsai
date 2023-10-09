import time

from Rosmaster_Lib import Rosmaster

class Platform:
    def __init__(self):
        self.master = Rosmaster('COM5')
        self.master.create_receive_threading()

    def straight_pid_distance(self, p, i, d):
        self.master.set_car_motion(0.2, 0, 0)
        time.sleep(1)
        self.master.set_car_motion(0, 0, 0)
        pass


if __name__ == 'main':
    pass
