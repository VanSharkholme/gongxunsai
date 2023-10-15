import sys
import time
from os import name as os_name
import threading
from Rosmaster_Lib import Rosmaster
import time

class DCMotor:
    def __init__(self, master, mid):
        self.master = master
        self.id = mid



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
        self.motor_lf = DCMotor(self.master, 1)
        self.motor_lb = DCMotor(self.master, 2)
        self.motor_rf = DCMotor(self.master, 3)
        self.motor_rb = DCMotor(self.master, 4)
        self.last_a1, self.last_a2, self.last_a3, self.last_a4 = self.master.get_motor_encoder()
        # self.condition.
    # def motor
        self.last_time = time.time()

    def get_cur_position(self):
        return 1, 2
        pass

    def pid_velocity(self, err):
        # out_put_vel = self.kp * err +
        pass

    def straight_pid_distance(self, x, y):
        cur_x, cur_y = self.get_cur_position()
        ex = x - cur_x
        ey = y - cur_y
        vx = self.pid_velocity(ex)
        vy = self.pid_velocity(ey)
        self.master.set_car_motion(0.15, 0, 0)
        # time.sleep(50)
        # self.master.set_car_motion(0, 0, 0)
        self.master.set
        print(time.time())
        pass

    def stop(self):
        self.master.set_car_motion(0, 0, 0)

    def odometry(self):
        a1, a2, a3, a4 = self.master.get_motor_encoder()
        if a1 != self.last_a1 or a2 != self.last_a2 or a3 != self.last_a3 or a4 != self.last_a4:
            now = time.time()
            v1, v2, v3, v4 = a1 - self.last_a1, a2 - self.last_a2, a3 - self.last_a3, a4 - self.last_a4
            vx, vy, vz = self.master.get_motion_data()
            self.last_a1, self.last_a2, self.last_a3, self.last_a4 = a1, a2, a3, a4
            print('\r', str(v1), str(v2), str(v3), str(v4), now-self.last_time, end="")
            self.last_time = now

        # print(vx, vy, vz, end='')

    def go(self):
        self.master.set_car_motion(-0.6, 0, 0)
        time.sleep(0.3)
        self.master.set_car_motion(0, 0.6, 0)
        time.sleep(2.5)
        self.stop()
        self.master.set_car_motion(0, 0.6, 0)
        time.sleep(2.5)
        self.stop()
        self.master.set_car_motion(0, 0.6, 0)
        time.sleep(0.3)
        self.master.set_car_motion(0, 0, 3.1415926535)
        time.sleep()
if __name__ == '__main__':
    p = Platform()
    p.master.create_receive_threading()
    # p.master.set_motor(0, 60, 0, 0)
    # # p.straight_pid_distance(0, 0, 0)
    # try:
    #     while True:
    #         p.odometry()
    #         time.sleep(0.1)
    # finally:
    #     p.stop()
    #     sys.exit()
    # pass
    p.master
