import platform_movement
import qrcode



def wait_start_signal():
    input()


wait_start_signal()
p = platform_movement.Platform()
p.straight_pid_distance(14, 0)
p.straight_pid_distance(0, 80)
obj_order = None
while not obj_order:
    obj_order = qrcode.qr_scan()
p.straight_pid_distance(0, 160)



