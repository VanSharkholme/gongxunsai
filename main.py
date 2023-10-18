import sys
import time
import platform_movement
import serial_screen
import target_yolo
import arm_definitions
import threading
from platform_movement import forward, back, left, right, ccw, cw, pi
import qrcode
from realsense_start import realsense_cam

cam = realsense_cam((1280, 720), 30)


def button_pressed():
    input()
    return True


lock = threading.Lock()

is_rotating = False


def check_rotating():
    global is_rotating
    with lock:
        for k in coordinates[0].keys():
            for l in range(len(coordinates[0][k])):
                if coordinates[0][k][l] - coordinates[1][k][l] > 0.01:
                    is_rotating = True
                    return
        is_rotating = False


def go_home(arm, obj=''):
    if obj == 'red_object':
        home = arm.forward_kinematics(-180, 0, 0, 90, 0, )
    elif obj == 'blue_object' or obj == 'green_object':
        home = arm.forward_kinematics(180, 0, 0, 90, 0)
    else:
        arm.Joint1.go_to_angle(0, arm.port)
        arm.Joint2.go_to_angle(0, arm.port)
        arm.Joint3.go_to_angle(0, arm.port)
        arm.Joint4.go_to_angle(90, arm.port)
        arm.Joint5.go_to_angle(-90, arm.port)
        return
    arm.go_to(home[0], home[1], home[2], home[3])


red = 1
green = 2
blue = 3
round1_ord = []
round2_ord = []
coordinates = [
    {
        'red_object': [0, 0, 0],
        'green_object': [0, 0, 0],
        'blue_object': [0, 0, 0],
        'red_target': [0, 0, 0],
        'green_target': [0, 0, 0],
        'blue_target': [0, 0, 0],
        'closest_object': None
    },
    {
        'red_object': [0, 0, 0],
        'green_object': [0, 0, 0],
        'blue_object': [0, 0, 0],
        'red_target': [0, 0, 0],
        'green_target': [0, 0, 0],
        'blue_target': [0, 0, 0],
        'closest_object': None
    }
]

object_holder_positions = {
    'red_object': [-143.19, -84.34, 14],
    'blue_object': [-166.23, 0, 14],
    'green_object': [-143.19, 84.34, 14]
}

visual_thread = threading.Thread(target=target_yolo.yolo_start, args=(cam, coordinates, lock))
rotation_thread = threading.Thread(target=check_rotating)

visual_thread.start()

p = platform_movement.Platform()
p.master.create_receive_threading()
arm = arm_definitions.Arm()
go_home(arm)
# movement_thread = threading.Thread(target=p.move, args=)
print('arm init')
sys.exit()

# TODO:wait for start signal
while not button_pressed():
    pass

p.move(back, 0.43, stop=False)
p.move(left, 1.5)
# time.sleep(1)
qr_msg = qrcode.qr_scan(cam)
round1_msg, round2_msg = qr_msg.strip().split('+')
for i in round1_msg:
    if int(i) == red:
        round1_ord.append('red_object')
    elif int(i) == green:
        round1_ord.append('green_object')
    elif int(i) == blue:
        round1_ord.append('blue_object')

for i in round2_msg:
    if int(i) == red:
        round2_ord.append('red_object')
    elif int(i) == green:
        round2_ord.append('green_object')
    elif int(i) == blue:
        round2_ord.append('blue_object')

p.move(left, 1.9)
# time.sleep(1)

for obj in round1_ord:
    while is_rotating:
        pass
    if obj == coordinates[0]['closest_object']:
        cur_coordinate = coordinates[0][obj]
        arm.go_to(cur_coordinate[0] * 100, cur_coordinate[1] * 100, cur_coordinate[2] * 100, 90)
        while arm.is_moving():
            pass
        arm.grip()
        while arm.is_moving():
            pass
        go_home(arm, obj)
        while arm.is_moving():
            pass
        place_coordinate = object_holder_positions[obj]
        arm.go_to(place_coordinate[0], place_coordinate[1], place_coordinate[2], 180)
        while arm.is_moving():
            pass
        arm.release()
        while arm.is_moving():
            pass
        go_home(arm)

p.move(left, 1)
time.sleep(0.4)
p.move(ccw, 0.894, pi)
time.sleep(0.4)
p.move(left, 1.8)
# time.sleep(3)

sys.exit()


p.move(left, 1.8)
time.sleep(0.4)
p.move(ccw, 0.878, pi)
time.sleep(0.4)
p.move(left, 1.8)
time.sleep(3)
p.move(right, 1.9)
time.sleep(0.4)
p.move(cw, 0.875, pi)
time.sleep(0.4)
p.move(right, 3.3)
time.sleep(0.4)
p.move(cw, 0.883, pi)
time.sleep(0.4)
p.move(right, 0.9)
time.sleep(5)
