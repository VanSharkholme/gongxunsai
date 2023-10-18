import os
import sys

import numpy as np
from numpy import sin, cos, arctan2, radians, degrees
from math import pi
from motor_control import Motor, MotorGroup, XL330, XL430, Port, COMM_SUCCESS


class Joint:
    def __init__(self, motor, parent, child, low_lim, up_lim, speed_lim):
        self.parent = parent
        self.child = child
        self.limit = [low_lim, up_lim]
        self.speed_limit = speed_lim
        self.motor = motor
        pass

    def get_cur_angle(self, port: Port):
        position, res, error = self.motor.read_info(self.motor.Present_Position, port)
        if res == COMM_SUCCESS:
            if self.motor.type == 'AX12A':
                angle = 300 * position / 1024
                n = angle // 300
                angle -= n * 300
                angle -= 150
            else:
                angle = 360 * position / 4096
                n = angle // 360
                angle -= n * 360
                angle -= 180
            return angle
        else:
            print(error)
            return -1

    def go_to_angle(self, angle, port: Port):
        if self.motor.type == 'AX12A':
            position = int((angle + 150) * 1024 / 300)
        else:
            position = int((angle + 180) * 4096 / 360)
        res = self.motor.send_instruction(self.motor.Torque_Ena, 1, port)
        res = self.motor.send_instruction(self.motor.Goal_Position, position, port)
        return res
        pass


class Link:
    def __init__(self, length):
        self.length = length
        pass


class EndEffector:
    def __init__(self, motor):
        self.elevation = 15.9
        self.x = 0
        self.y = 0
        self.z = 0
        self.roll = 0
        self.pitch = 0
        self.yaw = 0
        self.motor = motor



class Arm:
    def __init__(self):
        self.a = 18.75
        self.d2 = 25
        self.l1 = 86.75
        self.l2 = 86.75
        self.l3 = 71.75
        self.l4 = 87.7744
        self.Link0 = Link(0)
        self.Link1 = Link(self.a)
        self.Link2 = Link(self.l1)
        self.Link3 = Link(self.l2)
        self.Link4 = Link(self.l3)
        self.Link5 = Link(self.l4)
        self.Joint1 = Joint(XL430(1), self.Link0, self.Link1, -pi, pi, 0)
        self.Joint2 = Joint(XL430(2), self.Link1, self.Link2, 0, pi / 2, 20)
        self.Joint3 = Joint(XL430(3), self.Link2, self.Link3, -pi / 2, pi / 2, 20)
        self.Joint4 = Joint(XL430(4), self.Link3, self.Link4, -pi / 2, pi / 2, 40)
        self.Joint5 = Joint(XL330(5), self.Link4, self.Link5, -pi / 2, pi / 2, 0)
        self.port = Port('COM3') if os.name == 'nt' else Port('/dev/dynamixel')
        self.port.open_port()
        self.links = [self.Link0, self.Link1, self.Link2, self.Link3, self.Link4, self.Link5]
        self.joints = [self.Joint1, self.Joint2, self.Joint3, self.Joint4, self.Joint5]
        self.joint_init()
        self.eef = EndEffector(XL330(6))
        self.eef.motor.send_instruction(self.eef.motor.Torque_Ena, 1, self.port)
        self.eef.motor.send_instruction(self.eef.motor.Goal_Position, 2048, self.port)

    def joint_init(self):
        for joint in self.joints:
            motor = joint.motor
            try:
                motor.send_instruction(motor.Torque_Ena, 1, self.port)
                if motor.type == 'AX12A':
                    motor.send_instruction(motor.Moving_Speed, joint.speed_limit, self.port)
                else:
                    motor.send_instruction(motor.Profile_Accel, 10, self.port)
                    motor.send_instruction(motor.Profile_Velocity, 600, self.port)
            except:
                pass

    def arm_shutdown(self):
        for joint in self.joints:
            motor = joint.motor
            try:
                motor.send_instruction(motor.Torque_Ena, 0, self.port)
            except:
                pass
        self.port.close_port()

    def check_joint_angle(self, joint: Joint, angle):
        return angle >= joint.limit[0] and angle <= joint.limit[1]

    def forward_kinematics(self, theta1, theta2, theta3, theta4, theta5):
        theta1 = radians(theta1)
        theta2 = radians(theta2)
        theta3 = radians(theta3)
        theta4 = radians(theta4)
        theta5 = radians(theta5)

        self.eef.pitch = theta2 + theta3 + theta4 + theta5
        self.eef.yaw = theta1
        length = ((self.a + self.l1 * sin(theta2) + self.l2 * sin(theta2 + theta3) +
                   self.l3 * sin(theta2 + theta3 + theta4)) + self.l4 * sin(self.eef.pitch) -
                  self.eef.elevation * cos(self.eef.pitch))
        height = ((self.l1 * cos(theta2) + self.l2 * cos(theta2 + theta3) +
                   self.l3 * cos(theta2 + theta3 + theta4) + self.l4 * cos(self.eef.pitch)) +
                  self.eef.elevation * sin(self.eef.pitch))
        self.eef.x = length * cos(theta1)
        self.eef.y = length * sin(theta1)
        self.eef.z = height
        print('===================================================')
        print('x:', self.eef.x)
        print('y:', self.eef.y)
        print('z:', self.eef.z)
        print('roll:', degrees(self.eef.roll))
        print('pitch:', degrees(self.eef.pitch))
        print('yaw:', degrees(self.eef.yaw))
        print('===================================================')
        return self.eef.x, self.eef.y, self.eef.z, self.eef.pitch

    def inverse_kinematics(self, x, y, z, pitch, yaw):
        count = 0
        pitch = radians(pitch)
        yaw = radians(yaw)
        solutions = []
        solution = {
            'theta1': yaw,
            'theta2': None,
            'theta3': None,
            'theta4': None,
            'theta5': None,
        }
        gamma = 270
        step = 1
        solution_found = False
        valid_cur = False
        horizontal_distance = np.sqrt(x ** 2 + y ** 2)
        total_length = np.sqrt(x ** 2 + y ** 2 + z ** 2)
        if total_length > 349.7028884 or total_length < 40:
            return False, solution
        while gamma > -180:
            k1 = horizontal_distance - self.a - self.l4 * sin(pitch) + self.eef.elevation * cos(pitch)
            k2 = z - self.l4 * cos(pitch) - self.eef.elevation * sin(pitch)
            A1 = k1 - self.l3 * sin(np.radians(gamma))
            A2 = k2 - self.l3 * cos(np.radians(gamma))
            cos_theta3 = (A1 ** 2 + A2 ** 2 - self.l1 ** 2 - self.l2 ** 2) / (2 * self.l1 * self.l2)
            if cos_theta3 ** 2 > 1:
                gamma -= step
                continue
            sin_theta3 = np.sqrt(1 - cos_theta3 ** 2)

            theta3 = arctan2(sin_theta3, cos_theta3) # rad
            if not self.check_joint_angle(self.Joint3, theta3):
                gamma -= step
                continue
            theta2 = arctan2(A1, A2) - arctan2(self.l2 * sin_theta3, self.l1 + self.l2 * cos_theta3)

            if not self.check_joint_angle(self.Joint2, theta2):
                gamma -= step
                continue
            theta4 = np.radians(gamma) - theta2 - theta3
            if not self.check_joint_angle(self.Joint4, theta4):
                gamma -= step
                continue
            theta5 = pitch - np.radians(gamma)
            if not self.check_joint_angle(self.Joint5, theta5):
                gamma -= step
                continue
            solution_found = True
            solution['theta2'] = theta2
            solution['theta3'] = theta3
            solution['theta4'] = theta4
            solution['theta5'] = theta5
            count += 1
            break

            # solution_found = False
            gamma -= 1
        print('total solution nums:', count)
        print('===================================================')
        print('theta1:', np.degrees(solution['theta1']))
        print('theta2:', np.degrees(solution['theta2']))
        print('theta3:', np.degrees(solution['theta3']))
        print('theta4:', np.degrees(solution['theta4']))
        print('theta5:', np.degrees(solution['theta5']))
        print('===================================================')
        return solution_found, solution

    def go_to(self, x, y, z, pitch):
        yaw = np.degrees(arctan2(y, x))
        # pitch = np.degrees(pitch)
        res, solution = self.inverse_kinematics(x, y, z, pitch, yaw)
        if res:
            try:
                self.Joint1.go_to_angle(np.degrees(solution['theta1']), self.port)
            except:
                pass
            try:
                self.Joint2.go_to_angle(np.degrees(solution['theta2']), self.port)
            except:
                pass
            try:
                self.Joint3.go_to_angle(np.degrees(solution['theta3']), self.port)
            except:
                pass
            try:
                self.Joint4.go_to_angle(np.rad2deg(solution['theta4']), self.port)
            except:
                pass
            try:
                self.Joint5.go_to_angle(np.degrees(-solution['theta5']), self.port)
            except:
                pass
            # self.Joint5.go_to_angle(solution['theta1'])
        else:
            print('No Solution found')

    def grip(self):
        self.eef.motor.send_instruction(self.eef.motor.Goal_Position, 2455, self.port)

    def release(self):
        self.eef.motor.send_instruction(self.eef.motor.Goal_Position, 1700, self.port)

    def is_moving(self):
        for joint in self.joints:
            if joint.motor.read_info(joint.motor.Moving, self.port):
                return True
        if self.eef.motor.read_info(self.eef.motor.Moving, self.port):
            return True
        return False


if __name__ == '__main__':
    arm = Arm()
    # arm.forward_kinematics(10, 15, 20, 25, 30)

    try:
        arm.Joint1.go_to_angle(10, arm.port)
        arm.Joint2.go_to_angle(80, arm.port)
        arm.Joint3.go_to_angle(-30, arm.port)
        arm.Joint4.go_to_angle(60, arm.port)
        arm.Joint5.go_to_angle(60, arm.port)
        # arm.go_to(10, -10, 200, 90)
        # arm.go_to(220, 0, 200, 90)
    except:
        arm.arm_shutdown()
        sys.exit()
    # arm.forward_kinematics(
    #     np.degrees(solution['theta1']),
    #     np.degrees(solution['theta2']),
    #     np.degrees(solution['theta3']),
    #     np.degrees(solution['theta4']),
    #     np.degrees(solution['theta5'])
    # )
    # print(arm.Joint1.get_cur_angle(arm.port))
    # arm.Joint1.go_to_angle(45, arm.port)
    # arm.Joint2.go_to_angle(30, arm.port)
    # arm.Joint3.go_to_angle(45, arm.port)
    # arm.Joint4.go_to_angle(45, arm.port)

    # print(arm.Joint1.get_cur_angle(arm.port))
    finally:
        input()
        arm.arm_shutdown()
        arm.port.close_port()
        sys.exit()


