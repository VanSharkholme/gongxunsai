import time
import platform_movement
import serial_screen
import target_yolo
import arm_definitions
import threading

coordinates = {
    'red_object': [],
    'green_object': [],
    'blue_object': [],
    'red_target': [],
    'green_target': [],
    'blue_target': []
}
visual_thread = threading.Thread(target=target_yolo.yolo_start, args=(coordinates,))

def test(a):
    while True:
        a['aa'] = time.time()

d = {'aa': 1}

temp_thread = threading.Thread(target=test, args=(d,))
temp_thread.start()

time.sleep(1)
while True:
    print(d)
    time.sleep(1)
p = platform_movement.Platform()
p.master.create_receive_threading()
