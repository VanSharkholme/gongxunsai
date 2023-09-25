import pyrealsense2 as rs
import numpy as np
import cv2
from ultralytics import YOLO
from motor_control_no_annotations import *
import os
import sys

pipeline = rs.pipeline()
config = rs.config()
# 配置深度和颜色流
# 10、15或者30可选,20或者25会报错，其他帧率未尝试
# 配置颜色相机
config.enable_stream(rs.stream.color, 1280, 720, rs.format.bgr8, 30)
# 配置深度图像
config.enable_stream(rs.stream.depth, 1280, 720, rs.format.z16, 30)
# Start streaming
profile = pipeline.start(config)

# 创建对齐对象, rs.align 允许我们将深度帧与其他帧对齐, "align_to" 是计划对其深度帧的流类型
align_to = rs.stream.color
align = rs.align(align_to)

# YOLO部分
model = YOLO('runs/detect/train6/weights/best.pt')


def get_center(coordinates):
    return [int((coordinates[0] + coordinates[2]) / 2), int((coordinates[1] + coordinates[3]) / 2)]


m1 = XL330(4)
if os.name == 'nt':
    p = Port('COM3')
else:
    p = Port('/dev/ttyUSB0')
r = p.open_port()
m1.send_instruction(m1.Torque_Ena, 1, p)
m1.send_instruction(m1.Goal_Position, 2048, p)

try:
    while True:
        frames = pipeline.wait_for_frames()
        # 将深度框与颜色框对齐
        aligned_frames = align.process(frames)
        # 获取对齐帧
        aligned_depth_frame = aligned_frames.get_depth_frame()
        if not aligned_depth_frame:
            continue
        # depth_frame
        # color frames
        color_frame = aligned_frames.get_color_frame()
        if not color_frame:
            continue
        color_frame = np.asanyarray(color_frame.get_data())
        # cv2.imshow('2 color', color_frame)

        depth_intrinsics = aligned_depth_frame.profile.as_video_stream_profile().intrinsics

        predictions = model.predict(color_frame, device='cpu', show=False)
        name_dict = predictions[0].names
        classes = predictions[0].boxes.cls.cpu().numpy()
        coordinates = predictions[0].boxes.xyxy.cpu().numpy()
        for i in range(len(classes)):
            object_coordinate = coordinates[i]
            center = get_center(object_coordinate)
            distance = aligned_depth_frame.get_distance(center[0], center[1])
            spatial_coordinate = rs.rs2_deproject_pixel_to_point(depth_intrinsics, center, distance)
            xtext = 'x ' + str(round(spatial_coordinate[0], 5))
            ytext = 'y ' + str(round(spatial_coordinate[1], 5))
            ztext = 'z ' + str(round(spatial_coordinate[2], 5))
            # dtext = 'depth ' + str(distance)
            if classes[i] > 2:
                cv2.putText(color_frame, xtext, [center[0] + 2, center[1] - 15], cv2.FONT_HERSHEY_PLAIN, 1.25,
                            (255, 255, 255), 2)
                cv2.putText(color_frame, ytext, [center[0] + 2, center[1]], cv2.FONT_HERSHEY_PLAIN, 1.25,
                            (255, 255, 255), 2)
                cv2.putText(color_frame, ztext, [center[0] + 2, center[1] + 15], cv2.FONT_HERSHEY_PLAIN, 1.25,
                            (255, 255, 255), 2)
                # cv2.putText(color_frame, dtext, [center[0] + 2, center[1] + 20], cv2.FONT_HERSHEY_PLAIN, 0.75, (255, 255, 255), 2)

            if classes[i] == 3:
                cv2.circle(color_frame, center, 2, (0, 255, 0), -1)
            elif classes[i] == 4:
                cv2.circle(color_frame, center, 2, (0, 0, 255), -1)
            elif classes[i] == 5:
                cv2.circle(color_frame, center, 2, (255, 0, 0), -1)

        cv2.imshow('camera', color_frame)
        c = cv2.waitKey(1)

        # 如果按下ESC则关闭窗口（ESC的ascii码为27），同时跳出循环
        if c == 27:
            cv2.destroyAllWindows()
            break

finally:
    # Stop streaming
    m1.send_instruction(m1.Torque_Ena, 0, p)
    p.close_port()
    pipeline.stop()
    sys.exit()
