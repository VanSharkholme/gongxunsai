import sys
import threading

from ultralytics import YOLO
import cv2
import numpy as np
from realsense_start import realsense_cam
import pyrealsense2 as rs


def get_center(coordinates):
    return [int((coordinates[0] + coordinates[2]) / 2), int((coordinates[1] + coordinates[3]) / 2)]


def yolo_start(cam, res):
    # cam = realsense_cam((1280, 720), 30)
    global lock
    with (((((lock))))):
        model = YOLO('runs/detect/train13/weights/best.pt')

        transform_matrix = np.array([
            [0, -1 / np.sqrt(2), 1 / np.sqrt(2), 0],
            [-1, 0, 0, 0],
            [0, -1 / np.sqrt(2), -1 / np.sqrt(2), 0],
            [0, 0, 0, 1]
        ])
        transform_matrix = np.matrix(transform_matrix)
        print(transform_matrix)

        try:
            while True:
                frames = cam.get_frames()

                color_frame = frames['color']
                depth_frame = frames['depth']
                depth_intrinsics = cam.depth_intrinsics

                predictions = model.predict(color_frame, device='0', show=True)

                name_dict = predictions[0].names
                classes = predictions[0].boxes.cls.cpu().numpy()
                coordinates = predictions[0].boxes.xyxy.cpu().numpy()
                confs = predictions[0].boxes.conf.cpu().numpy()
                # if len(classes) > 0:
                #     pass
                for k in res[0].keys():
                    if k == 'closest_object':
                        res[1][k] = res[0][k]
                    else:
                        for i in range(len(res[0][k])):
                            res[1][k][i] = res[0][k][i]
                        for i in range(len(res[0][k])):
                            res[0][k][i] = -1

                max_d = 999

                for i in range(len(classes)):
                    if confs[i] < 0.7:
                        continue
                    object_coordinate = coordinates[i]
                    center = get_center(object_coordinate)
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
                    x = np.round(new_coordinate.getA()[0][0], 5)
                    y = np.round(new_coordinate.getA()[1][0], 5)
                    z = -np.round(spatial_coordinate[2] * np.sqrt(2) - new_coordinate.getA()[0][0], 5)
                    x += 0.03566
                    y += 0.0325
                    z += 0.20466
                    xtext = 'x ' + str(x)
                    ytext = 'y ' + str(y)
                    ztext = 'z ' + str(z)
                    #
                    # xtext = 'x ' + str(round(spatial_coordinate[0], 5))
                    # ytext = 'y ' + str(round(spatial_coordinate[1], 5))
                    # ztext = 'z ' + str(round(spatial_coordinate[2], 5))
                    if name_dict[classes[i]] == 'red_top':
                        res[0]['red_object'][0] = x
                        res[0]['red_object'][1] = y
                        res[0]['red_object'][2] = z
                    elif name_dict[classes[i]] == 'blue_top':
                        res[0]['blue_object'][0] = x
                        res[0]['blue_object'][1] = y
                        res[0]['blue_object'][2] = z
                    elif name_dict[classes[i]] == 'green_top':
                        res[0]['green_object'][0] = x
                        res[0]['green_object'][1] = y
                        res[0]['green_object'][2] = z
                    elif name_dict[classes[i]] == 't_red':
                        res[0]['red_target'][0] = x
                        res[0]['red_target'][1] = y
                        res[0]['red_target'][2] = z
                    elif name_dict[classes[i]] == 't_blue':
                        res[0]['blue_target'][0] = x
                        res[0]['blue_target'][1] = y
                        res[0]['blue_target'][2] = z
                    elif name_dict[classes[i]] == 't_green':
                        res[0]['green_target'][0] = x
                        res[0]['green_target'][1] = y
                        res[0]['green_target'][2] = z

                    if (name_dict[classes[i]] == 'red_top' or name_dict[classes[i]] == 'blue_top' or
                            name_dict[classes[i]] == 'green_top') and spatial_coordinate[2] < max_d:
                        max_d = spatial_coordinate[2]
                        if name_dict[classes[i]] == 'red_top':
                            res[0]['closest_object'] = 'red_object'
                        elif name_dict[classes[i]] == 'blue_top':
                            res[0]['closest_object'] = 'blue_object'
                        elif name_dict[classes[i]] == 'green_top':
                            res[0]['closest_object'] = 'green_object'
                    else:
                        res[0]['closest_object'] = None
                    # print(str(classes[i]) + ':' + xtext + '|' + ytext + '|' + ztext)

                    # cv2.putText(color_frame, xtext, [center[0] + 2, center[1] - 15], cv2.FONT_HERSHEY_PLAIN, 1.25,
                    #             (255, 255, 255), 2)
                    # cv2.putText(color_frame, ytext, [center[0] + 2, center[1]], cv2.FONT_HERSHEY_PLAIN, 1.25,
                    #             (255, 255, 255), 2)
                    # cv2.putText(color_frame, ztext, [center[0] + 2, center[1] + 15], cv2.FONT_HERSHEY_PLAIN, 1.25,
                    #             (255, 255, 255), 2)
                    #
                    # if classes[i] == 0:
                    #     cv2.circle(color_frame, center, 2, (0, 255, 0), -1)
                    # elif classes[i] == 1:
                    #     cv2.circle(color_frame, center, 2, (0, 0, 255), -1)
                    # elif classes[i] == 2:
                    #     cv2.circle(color_frame, center, 2, (255, 0, 0), -1)

                # cv2.imshow('camera', color_frame)
                print('===========================================================')
                print(res[0])
                print(res[1])
                print('===========================================================')
                # c = cv2.waitKey(1)
                #
                # if c == 27:
                #     cv2.destroyAllWindows()
                #     cam.stop()
                #     sys.exit()
                #     break

        finally:
            cam.stop()


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
    yolo_start(cam, res)
