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
        self.vx = 0
        self.vy = 0
        self.vz = 0
        self.dx = 0
        self.dy = 0
        self.dz = 0
        self.motor_lf = DCMotor(self.master, 1)
        self.motor_lb = DCMotor(self.master, 2)
        self.motor_rf = DCMotor(self.master, 3)
        self.motor_rb = DCMotor(self.master, 4)
        self.ax = []
        self.ay = []
        self.az = []
        self.smoothed_ax = 0
        self.smoothed_ay = 0
        self.last_a1, self.last_a2, self.last_a3, self.last_a4 = self.master.get_motor_encoder()
        self.d = threading.Thread(target=self.get_cur_position)
        # self.condition.
    # def motor
        self.last_time = time.time()
        self.lock = threading.Lock()

    def get_smoothed_sensor(self):
        while True:
            x, y, z = self.master.get_accelerometer_data()
            if len(self.ax) > 10:
                del(self.ax[0])
            self.ax.append(x)
            if len(self.ay) > 10:
                del(self.ay[0])
            self.ax.append(x)
            self.lock.acquire()
            self.smoothed_ax = sum(self.ax) / len(self.ax)
            self.smoothed_ay = sum(self.ay) / len(self.ay)
            self.lock.release()


    def get_cur_position(self):
        while True:
            self.lock.acquire()
            ax = self.smoothed_ax
            ay = self.smoothed_ay
            self.lock.release()
            self.vx += ax * 0.1
            self.vy += ay * 0.1
            self.dx += self.vx * 0.1
            self.dy += self.vy * 0.1
            time.sleep(0.1)
            print(ax, ay, '|', self.vx, self.vy, '|', self.dx, self.dy, '\r', sep=' ', end='')

        pass

    def pid_velocity(self, err):
        # out_put_vel = self.kp * err +
        pass

    def straight_pid_distance(self, x, y):

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
        time.sleep(0.43)
        self.master.set_car_motion(0, 0.6, 0)
        time.sleep(1.5)
        self.stop()
        time.sleep(1)
        self.master.set_car_motion(0, 0.6, 0)
        time.sleep(1.9)
        self.stop()
        time.sleep(1)
        self.master.set_car_motion(0, 0.6, 0)
        time.sleep(1)
        self.stop()
        time.sleep(0.4)
        self.master.set_car_motion(0, 0, 3.1415926535)
        time.sleep(0.894)
        self.stop()
        time.sleep(0.4)
        self.master.set_car_motion(0, 0.6, 0)
        time.sleep(1.8)
        self.stop()
        time.sleep(3)
        self.master.set_car_motion(0, 0.6, 0)
        time.sleep(1.8)
        self.stop()
        time.sleep(0.4)
        self.master.set_car_motion(0, 0, 3.1415926535)
        time.sleep(0.878)
        self.stop()
        time.sleep(0.4)
        self.master.set_car_motion(0, 0.6, 0)
        time.sleep(1.8)
        self.stop()
        time.sleep(3)
        self.master.set_car_motion(0, -0.6, 0)
        time.sleep(1.9)
        self.stop()
        time.sleep(0.4)
        self.master.set_car_motion(0, 0, -3.1415926535)
        time.sleep(0.875)
        self.stop()
        time.sleep(0.4)
        self.master.set_car_motion(0, -0.6, 0)
        time.sleep(3.3)
        self.stop()
        time.sleep(0.4)
        self.master.set_car_motion(0, 0, -3.1415926535)
        time.sleep(0.883)
        self.stop()
        time.sleep(0.4)
        self.master.set_car_motion(0, -0.6, 0)
        time.sleep(0.9)
        self.stop()
        time.sleep(5)
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
    p.go()
