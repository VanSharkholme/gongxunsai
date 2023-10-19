import sys
import threading
import time
from ultralytics import YOLO
import cv2
import numpy as np
from realsense_start import realsense_cam
import pyrealsense2 as rs


class VisualThread(threading.Thread):

    def __init__(self, cam, ready, res, lock):
        super().__init__()
        self.__flag = threading.Event()  # 用于暂停线程的标识
        self.__flag.set()  # 设置为True
        self.__running = threading.Event()  # 用于停止线程的标识
        self.__running.set()  # 将running设置为True
        self.cam = cam
        self.ready = ready
        self.res = res
        self.lock = lock
        self.cnt = {
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

    def run(self):
        model = YOLO('runs/detect/train13/weights/best.pt')
        ready_cnt = 5

        transform_matrix = np.array([
            [0, -1 / np.sqrt(2), 1 / np.sqrt(2), 0],
            [-1, 0, 0, 0],
            [0, -1 / np.sqrt(2), -1 / np.sqrt(2), 0],
            [0, 0, 0, 1]
        ])
        transform_matrix = np.matrix(transform_matrix)
        print(transform_matrix)

        try:
            while self.__running.is_set():
                self.__flag.wait()  # 为True时立即返回, 为False时阻塞直到内部的标识位为True后返回
                frames = self.cam.get_frames()

                color_frame = frames['color']
                depth_frame = frames['depth']
                depth_intrinsics = self.cam.depth_intrinsics

                predictions = model.predict(color_frame, device='0', show=True, verbose=False)

                if ready_cnt > 0:
                    ready_cnt -= 1
                elif ready_cnt == 0:
                    self.ready[0] = True
                    ready_cnt -= 1
                else:
                    pass

                name_dict = predictions[0].names
                classes = predictions[0].boxes.cls.cpu().numpy()
                coordinates = predictions[0].boxes.xyxy.cpu().numpy()
                confs = predictions[0].boxes.conf.cpu().numpy()
                # if len(classes) > 0:
                #     pass
                for k in self.res[0].keys():
                    if k == 'closest_object':
                        self.res[1][k] = self.res[0][k]
                    else:
                        for i in range(len(self.res[0][k])):
                            self.res[1][k][i] = self.res[0][k][i]


                max_d = 999

                self.cnt = {
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

                for i in range(len(classes)):
                    cls = classes[i]
                    if confs[i] < 0.8:
                        continue
                    self.cnt[name_dict[cls]] += 1

                self.ready[1] = self.cnt['red_top'] <= 1 and self.cnt['blue_top'] <= 1 and self.cnt['green_top'] <= 1

                for i in range(len(classes)):
                    if confs[i] < 0.7:
                        continue
                    object_coordinate = coordinates[i]
                    center = self.get_center(object_coordinate)
                    distance = depth_frame.get_distance(center[0], center[1])
                    spatial_coordinate = rs.rs2_deproject_pixel_to_point(depth_intrinsics, center, distance)
                    raw_coordinate = np.array([
                        [spatial_coordinate[0]],
                        [spatial_coordinate[1]],
                        [spatial_coordinate[2]],
                        [1]
                    ])
                    raw_coordinate = np.matrix(raw_coordinate)
                    new_coordinate = transform_matrix * raw_coordinate
                    x = new_coordinate.getA()[0][0]
                    y = new_coordinate.getA()[1][0]
                    z = -(spatial_coordinate[2] * np.sqrt(2) - new_coordinate.getA()[0][0])
                    x += 0.025
                    y += 0.017
                    z += 0.20466
                    xtext = 'x ' + str(x)
                    ytext = 'y ' + str(y)
                    ztext = 'z ' + str(z)
                    time.sleep(0.015)
                    #
                    # xtext = 'x ' + str(round(spatial_coordinate[0], 5))
                    # ytext = 'y ' + str(round(spatial_coordinate[1], 5))
                    # ztext = 'z ' + str(round(spatial_coordinate[2], 5))
                    with self.lock:
                        if name_dict[classes[i]] == 'red_top':
                            self.res[0]['red_object'][0] = x
                            self.res[0]['red_object'][1] = y
                            self.res[0]['red_object'][2] = z
                        elif name_dict[classes[i]] == 'blue_top':
                            self.res[0]['blue_object'][0] = x
                            self.res[0]['blue_object'][1] = y
                            self.res[0]['blue_object'][2] = z
                        elif name_dict[classes[i]] == 'green_top':
                            self.res[0]['green_object'][0] = x
                            self.res[0]['green_object'][1] = y
                            self.res[0]['green_object'][2] = z
                        elif name_dict[classes[i]] == 't_red':
                            self.res[0]['red_target'][0] = x
                            self.res[0]['red_target'][1] = y
                            self.res[0]['red_target'][2] = z
                        elif name_dict[classes[i]] == 't_blue':
                            self.res[0]['blue_target'][0] = x
                            self.res[0]['blue_target'][1] = y
                            self.res[0]['blue_target'][2] = z
                        elif name_dict[classes[i]] == 't_green':
                            self.res[0]['green_target'][0] = x
                            self.res[0]['green_target'][1] = y
                            self.res[0]['green_target'][2] = z

                        if (name_dict[classes[i]] == 'red_top' or name_dict[classes[i]] == 'blue_top' or
                            name_dict[classes[i]] == 'green_top') and x < max_d:
                            max_d = x
                            if name_dict[classes[i]] == 'red_top':
                                self.res[0]['closest_object'] = 'red_object'
                            elif name_dict[classes[i]] == 'blue_top':
                                self.res[0]['closest_object'] = 'blue_object'
                            elif name_dict[classes[i]] == 'green_top':
                                self.res[0]['closest_object'] = 'green_object'
                            else:
                                self.res[0]['closest_object'] = None
                    # print(str(classes[i]) + ':' + xtext + '|' + ytext + '|' + ztext)

                    # print(self.cnt)

                #     cv2.putText(color_frame, xtext, [center[0] + 2, center[1] - 15], cv2.FONT_HERSHEY_PLAIN, 1.25,
                #                 (255, 255, 255), 2)
                #     cv2.putText(color_frame, ytext, [center[0] + 2, center[1]], cv2.FONT_HERSHEY_PLAIN, 1.25,
                #                 (255, 255, 255), 2)
                #     cv2.putText(color_frame, ztext, [center[0] + 2, center[1] + 15], cv2.FONT_HERSHEY_PLAIN, 1.25,
                #                 (255, 255, 255), 2)
                #
                #     if classes[i] == 0:
                #         cv2.circle(color_frame, center, 2, (0, 255, 0), -1)
                #     elif classes[i] == 1:
                #         cv2.circle(color_frame, center, 2, (0, 0, 255), -1)
                #     elif classes[i] == 2:
                #         cv2.circle(color_frame, center, 2, (255, 0, 0), -1)
                #
                # cv2.imshow('camera', color_frame)

                # print('===========================================================')
                # print(res[0])
                # print(res[1])
                # print('===========================================================')

                # c = cv2.waitKey(1)
                #
                # if c == 27:
                #     cv2.destroyAllWindows()
                #     cam.stop()
                #     sys.exit()
                #     break
            time.sleep(0.1)
        finally:
            self.cam.stop()

    def pause(self):
        self.__flag.clear()  # 设置为False, 让线程阻塞

    def resume(self):
        self.__flag.set()  # 设置为True, 让线程停止阻塞

    def stop(self):
        self.__flag.set()  # 将线程从暂停状态恢复, 如何已经暂停的话
        self.__running.clear()  # 设置为False

    def get_center(self, coordinates):
        return [int((coordinates[0] + coordinates[2]) / 2), int((coordinates[1] + coordinates[3]) / 2)]


if __name__ == '__main__':
    cam = realsense_cam((1280, 720), 30)
    res = [
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
    lock = threading.Lock()
    ready = [False, False]
    is_rotating = [True]
    vthread = VisualThread(cam=cam, ready=ready, res=res, lock=lock)
    vthread.start()


    def check_rotating(coordinates, is_rotating, lock):
        while True:
            with lock:
                for k in coordinates[0].keys():
                    if k == 'closest_object':
                        continue
                    for l in range(len(coordinates[0][k])):
                        if coordinates[0][k][l] - coordinates[1][k][l] > 0.001:
                            print('is_rotating', is_rotating, '\r', end='')
                            is_rotating[0] = True
                is_rotating[0] = False
                print('is_rotating', is_rotating, '\r', end='')


    # rotation_thread = threading.Thread(target=check_rotating, args=(res, is_rotating, lock))
    # rotation_thread.start()
    check_rotating(res, is_rotating, lock)
    # while True:
    #     print(is_rotating)
    #     time.sleep(1)

    # while True:
    #     print(ready)
    #     time.sleep(1)
