import pyrealsense2 as rs
import numpy as np
import cv2 as cv

imu_pipeline = rs.pipeline()
imu_config = rs.config()
imu_config.enable_stream(rs.stream.accel, rs.format.motion_xyz32f, 200)
imu_config.enable_stream(rs.stream.gyro, rs.format.motion_xyz32f, 200)

imu_pipeline.start(imu_config)

def get_perspective_matrix(frames: rs.composite_frame):
    imu_frame = frames.first(rs.stream.accel, rs.format.motion_xyz32f)
    gyro_frame = frames.first(rs.stream.gyro, rs.format.motion_xyz32f)

    # Get data from IMU frames
    accel_data = imu_frame.as_motion_frame().get_motion_data()
    gyro_data = gyro_frame.as_motion_frame().get_motion_data()

    # Calculate roll, pitch, and yaw angles using sensor fusion
    roll = np.arctan2(accel_data.x, np.sqrt(accel_data.y ** 2 + accel_data.z ** 2))
    pitch = np.arctan2(-accel_data.y, np.sqrt(accel_data.x ** 2 + accel_data.z ** 2))
    yaw = np.arctan2(accel_data.z, np.sqrt(accel_data.x ** 2 + accel_data.y ** 2))

    # Convert angles from radians to degrees
    roll_deg = np.degrees(roll)
    pitch_deg = np.degrees(pitch)
    yaw_deg = np.degrees(yaw)
    pass

    # Convert angles to radians
    roll_rad = np.radians(roll_deg)
    pitch_rad = np.radians(pitch_deg)
    yaw_rad = np.radians(yaw_deg)

    # Rotation matrices around each axis
    rot_x = np.array([[1, 0, 0],
                      [0, np.cos(roll_rad), -np.sin(roll_rad)],
                      [0, np.sin(roll_rad), np.cos(roll_rad)]])

    rot_y = np.array([[np.cos(pitch_rad), 0, np.sin(pitch_rad)],
                      [0, 1, 0],
                      [-np.sin(pitch_rad), 0, np.cos(pitch_rad)]])

    rot_z = np.array([[np.cos(yaw_rad), -np.sin(yaw_rad), 0],
                      [np.sin(yaw_rad), np.cos(yaw_rad), 0],
                      [0, 0, 1]])

    # Combine the rotation matrices to get the total rotation matrix
    rotation_matrix = np.dot(np.dot(rot_z, rot_y), rot_x)

    # Define the output dimensions (width and height) after transformation
    output_width = 1280
    output_height = 720

    # Calculate the perspective transformation matrix
    transformation_matrix = cv.getAffineTransform(np.float32([[0, 0], [1, 0], [0, 1]]),
                                                   np.float32([[0, 0], [output_width, 0], [0, output_height]]))

    # Apply the rotation matrix to the perspective transformation matrix
    final_transformation_matrix = rot_x

    print(final_transformation_matrix, end='\r', flush=True)

while True:
    frames = imu_pipeline.wait_for_frames()
    get_perspective_matrix(frames)