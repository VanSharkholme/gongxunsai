import cv2 as cv
import pyrealsense2 as rs
def get_coordinate(center:tuple[int, int], depth:float, depth_intrinsic:rs.stream_profile.in)->list[float, float, float]:
    a = depth_intrinsic.as_video_stream_profile()
    print(type(a))

pipeline = rs.pipeline()
config = rs.config()
config.enable_stream(rs.stream.color, 1280, 720, rs.format.bgr8, 30)

pipeline.start(config)
while True:
    frame = pipeline.wait_for_frames()
    get_coordinate((1,1), 12.5, frame)