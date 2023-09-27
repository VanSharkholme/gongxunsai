import numpy as np
import pyrealsense2 as rs
import cv2

class realsense_cam:
    def __init__(self, resolution:tuple, framerate:int):
        self.pipeline = rs.pipeline()
        self.config = rs.config()
        self.width = resolution[0]
        self.height = resolution[1]
        self.framerate = framerate
        self.config.enable_stream(rs.stream.color, self.width, self.height, rs.format.bgr8, self.framerate)
        self.config.enable_stream(rs.stream.depth, self.width, self.height, rs.format.z16, self.framerate)
        self.profile = self.pipeline.start(self.config)
        self.align_to = rs.stream.color
        self.align = rs.align(self.align_to)
        self.last_frame = {}
        self.depth_intrinsics = None

    def get_frames(self):
        try:
            frames = self.pipeline.wait_for_frames()
            aligned_frames = self.align.process(frames)
            depth_frame = aligned_frames.get_depth_frame()
            if depth_frame:
                self.last_frame['depth'] = depth_frame
                self.depth_intrinsics = depth_frame.profile.as_video_stream_profile().intrinsics
            color_frame = aligned_frames.get_color_frame()
            if color_frame:
                color_frame = np.asanyarray(color_frame.get_data())
                self.last_frame['color'] = color_frame
            return self.last_frame
        except:
            return None

    def stop(self):
        self.pipeline.stop()
