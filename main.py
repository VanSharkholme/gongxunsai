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

is_rotating = [False]


def check_rotating(coordinates, is_rotating, lock):
    while True:
        with lock:
            for k in coordinates[0].keys():
                if k == 'closest_object':
                    continue
                for l in range(len(coordinates[0][k])):
                    if coordinates[0][k][l] - coordinates[1][k][l] > 0.0015:
                        # print('is_rotating', is_rotating, '\r', end='')
                        is_rotating[0] = True
            is_rotating[0] = False
            # print('is_rotating', is_rotating, '\r', end='')


def go_home(arm, obj=''):
    if obj == 'red_object':
        arm.Joint2.go_to_angle(0, arm.port)
        arm.Joint3.go_to_angle(0, arm.port)
        arm.Joint4.go_to_angle(90, arm.port)
        arm.Joint5.go_to_angle(0, arm.port)
        arm.Joint1.go_to_angle(-145, arm.port)
    elif obj == 'blue_object' or obj == 'green_object':
        arm.Joint2.go_to_angle(0, arm.port)
        arm.Joint3.go_to_angle(0, arm.port)
        arm.Joint4.go_to_angle(90, arm.port)
        arm.Joint5.go_to_angle(0, arm.port)
        arm.Joint1.go_to_angle(180, arm.port)
    else:
        arm.Joint2.go_to_angle(0, arm.port)
        arm.Joint3.go_to_angle(0, arm.port)
        arm.Joint4.go_to_angle(90, arm.port)
        arm.Joint5.go_to_angle(0, arm.port)
        arm.Joint1.go_to_angle(0, arm.port)


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
    'red_object': [-143.23, -83.34, 16],
    # 'red_object': [-1, 3.72, 14.04, 85.24, -57],
    'blue_object': [-166.23, 0, 16],
    # 'blue_object': [180, 4.15, 13.5, 85.3389, -60],
    'green_object': [-143.19, 83.34, 16],
    # 'green_object': [150.23, 3.72, 14.04, 85.24, -57]
}

cnt = {
        'blue': 0,
        'green': 0,
        'red': 0,
        'blue_top': 0,
        'green_top': 0,
        'red_top': 0,
        't_blue': 0,
        't_green': 0,
        't_red': 0
    }

grip_coordinate = [0.2386135, 0.011082, 0.012394]

visual_ready = [False, False]
visual_thread = target_yolo.VisualThread(cam=cam, ready=visual_ready, res=coordinates, lock=lock)
# rotation_thread = threading.Thread(target=check_rotating, args=(coordinates, is_rotating, lock))
visual_thread.start()

while not visual_ready[0]:
    time.sleep(0.1)
    pass

visual_thread.pause()
# p = platform_movement.Platform()
# p.master.create_receive_threading()
arm = arm_definitions.Arm()
go_home(arm, 'blue_object')
go_home(arm, 'blue_object')
# movement_thread = threading.Thread(target=p.move, args=)
print('arm init')
# input()

# TODO:wait for start signal
while not button_pressed():
    pass

# p.move(back, 0.43, stop=False)
# p.move(left, 1.5)
# time.sleep(1)
# rotation_thread.start()
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

# p.move(left, 1.9)
# time.sleep(1)
print('pick place')
visual_thread.resume()
if coordinates[0]['red_object'] == [-1, -1, -1] or coordinates[0]['blue_object'] == [-1, -1, -1] or \
        coordinates[0]['green_object'] == [-1, -1, -1]:
    # p.move(back, 0.15)
    pass

i = 0
thresh = 0.04
while i in range(len(round1_ord)):
    obj = round1_ord[i]
    print(obj)
    cur_coordinate = coordinates[0][obj]
    while abs(cur_coordinate[0] - grip_coordinate[0]) > thresh or abs(cur_coordinate[1] - grip_coordinate[1]) > thresh or \
            abs(cur_coordinate[2] - grip_coordinate[2]) > thresh or coordinates[0]['closest_object'] != obj:
        print('not ideal object', coordinates[0]['closest_object'], '\r', sep='', end='')
        pass
    time.sleep(0.5)
    if abs(cur_coordinate[0] - grip_coordinate[0]) > thresh or abs(cur_coordinate[1] - grip_coordinate[1]) > thresh or \
        abs(cur_coordinate[2] - grip_coordinate[2]) > thresh or coordinates[0]['closest_object'] != obj:
        continue
    visual_thread.pause()
    arm.Joint5.go_to_angle(0, arm.port)
    arm.Joint1.go_to_angle(0, arm.port)
    arm.release()
    time.sleep(1)
    arm.go_to(cur_coordinate[0] * 1000, cur_coordinate[1] * 1000, cur_coordinate[2] * 1000+80, 90)

    time.sleep(0.3)
    arm.go_to(cur_coordinate[0] * 1000, cur_coordinate[1] * 1000, cur_coordinate[2] * 1000 - 10, 90)
    time.sleep(0.3)
    arm.grip()
    time.sleep(0.5)
    go_home(arm, obj)
    time.sleep(2)
    # while arm.is_moving():
    #     pass
    # go_home(arm, obj)
    # while arm.is_moving():
    #     pass
    place_coordinate = object_holder_positions[obj]
    arm.go_to(place_coordinate[0], place_coordinate[1], place_coordinate[2]+70, 170)
    # place = object_holder_positions[obj]
    # arm.go_to_angle(place[0], place[1], place[2], place[3], place[4])
    time.sleep(2)
    arm.release()
    time.sleep(0.2)
    go_home(arm, 'blue_object')
    i += 1
    visual_thread.resume()

sys.exit()

p.move(left, 1)
time.sleep(0.4)
p.move(ccw, 0.894, pi)
time.sleep(0.4)
p.move(left, 1.8)
# time.sleep(3)

# for obj in round1




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
