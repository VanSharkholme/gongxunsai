import sys
from ultralytics import YOLO
import cv2
import numpy as np
from realsense_start import *

cam = realsense_cam((1280, 720), 30)

model = YOLO('runs/detect/train8/weights/best.pt')


# try:
while True:
    frames = cam.get_frames()

    color_frame = frames['color']

    depth_intrinsics = cam.depth_intrinsics

    predictions = model.predict(color_frame, device=0, show=True)

# except:
#     pipeline.stop()
#     sys.exit()
