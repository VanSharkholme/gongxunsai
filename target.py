import cv2 as cv
import pyrealsense2 as rs
import numpy as np

def filter(frame, area_proportion, min_area, hw_proportion):
    frame = cv.blur(frame, (3, 3))
    edge_frame = cv.Canny(frame, 50, 150, apertureSize=3)
    contours_frame, hierarchy = cv.findContours(edge_frame, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
    valid_box = []
    for contour in contours_frame:
        rect = cv.minAreaRect(contour)
        (x, y), (w, h), theta = rect
        rect_area = w * h
        con_area = cv.contourArea(contour)
        if con_area == 0:
            continue
        # box = cv.boxPoints(rect)
        # pt1, pt2, pt3, pt4 = box
        if (rect_area / con_area < area_proportion
                and con_area > min_area
                and (w / h > hw_proportion or h / w > hw_proportion)):
            valid_box.append(rect)
        #     pass
        #     if np.sqrt((pt1[0]-pt2[0])**2 + (pt1[1]-pt2[1])**2) > np.sqrt((pt3[0]-pt2[0])**2 + (pt3[1]-pt2[1])**2):
        #         mid1 = (int(x + (pt2[0]-pt1[0]) / 2), int(y - (pt2[1]-pt1[1]) / 2))
        #         mid2 = (int(x - (pt2[0]-pt1[0]) / 2), int(y + (pt2[1]-pt1[1]) / 2))
        #     else:
        #         mid1 = (int(x - (pt3[0]-pt2[0]) / 2), int(y - (pt2[1]-pt3[1]) / 2))
        #         mid2 = (int(x + (pt3[0]-pt2[0]) / 2), int(y + (pt2[1]-pt3[1]) / 2))
            # pt1 = box[opposite_corners_indices[0]]
            # pt2 = box[opposite_corners_indices[1]]
            # cv.drawContours(frame_mask, contour, -1, (255, 255, 255), cv.FILLED)
            # valid_box.append(box)
            # cv.rotatedRectangleIntersection()
            # cv.line(frame_mask, mid1, mid2, (255, 255, 255), 2)
        # cv.drawContours(frame_mask, valid_contour, -1, 255, -1)
    return valid_box

pipeline = rs.pipeline()
config = rs.config()

config.enable_stream(rs.stream.color, 1280, 720, rs.format.bgr8, 30)
config.enable_stream(rs.stream.depth, 1280, 720, rs.format.z16, 30)
pipeline.start(config)

align_to = rs.stream.color
align = rs.align(align_to)


kernel1 = cv.getStructuringElement(cv.MORPH_RECT, (3, 1), (-1, -1))
kernel2 = cv.getStructuringElement(cv.MORPH_RECT, (1, 3), (-1, -1))
kernel3 = cv.getStructuringElement(cv.MORPH_RECT, (3, 3), (-1, -1))
try:
    while True:
        frames = pipeline.wait_for_frames()
        aligned_frames = align.process(frames)

        color_frame = np.asanyarray(aligned_frames.get_color_frame().get_data())
        depth_frame = aligned_frames.get_depth_frame()

        grayed_frame = cv.cvtColor(color_frame, cv.COLOR_BGR2GRAY)

        closed = cv.morphologyEx(grayed_frame, cv.MORPH_CLOSE, kernel3, iterations=5)
        grayed_frame = cv.bitwise_not(closed - grayed_frame)
        grayed_frame = cv.morphologyEx(grayed_frame, cv.MORPH_OPEN, kernel3)
        cv.normalize(grayed_frame, grayed_frame, 0, 200, cv.NORM_MINMAX)

        ret, binary_frame = cv.threshold(grayed_frame, 100, 255, cv.THRESH_BINARY_INV | cv.THRESH_OTSU)

        hori = cv.morphologyEx(binary_frame, cv.MORPH_OPEN, kernel1, iterations=2)
        hori = cv.dilate(hori, kernel2, iterations=3)
        hori = cv.morphologyEx(hori, cv.MORPH_OPEN, kernel1, iterations=9)
        verti = cv.morphologyEx(binary_frame, cv.MORPH_OPEN, kernel2, iterations=4)
        verti = cv.dilate(verti, kernel1, iterations=3)
        verti = cv.morphologyEx(verti, cv.MORPH_OPEN, kernel2, iterations=9)
        hori_boxes = filter(hori, 1.5, 350, 7)
        verti_boxes = filter(verti, 1.8, 380, 7)
        centers = []
        if len(hori_boxes) * len(verti_boxes) > 0:
            for hori_box in hori_boxes:
                for verti_box in verti_boxes:
                    ret, intersect = cv.rotatedRectangleIntersection(hori_box, verti_box)
                    if ret:
                        sum_x = 0
                        sum_y = 0
                        for pt in intersect:
                            sum_x += pt[0][0]
                            sum_y += pt[0][1]
                        center_x = int(sum_x / len(intersect))
                        center_y = int(sum_y / len(intersect))
                        centers.append((center_x, center_y))
                    pass

        depth_intrinsics = depth_frame.profile.as_video_stream_profile().intrinsics
        for center in centers:
            cv.circle(color_frame, center, 2, (0, 255, 0), -1)
            distance = depth_frame.get_distance(center[0], center[1])
            spatial_coordinate = rs.rs2_deproject_pixel_to_point(depth_intrinsics, center, distance)
            xtext = 'x ' + str(round(spatial_coordinate[0], 5))
            ytext = 'y ' + str(round(spatial_coordinate[1], 5))
            ztext = 'z ' + str(round(spatial_coordinate[2], 5))
            cv.putText(color_frame, xtext, [center[0] + 2, center[1] - 15], cv.FONT_HERSHEY_PLAIN, 1.25, (255, 255, 255),
                        2)
            cv.putText(color_frame, ytext, [center[0] + 2, center[1]], cv.FONT_HERSHEY_PLAIN, 1.25, (255, 255, 255), 2)
            cv.putText(color_frame, ztext, [center[0] + 2, center[1] + 15], cv.FONT_HERSHEY_PLAIN, 1.25, (255, 255, 255),
                        2)
        # result = cv.bitwise_or(hori, verti)

        # lines = get_lines(result)
        # for line in lines:
        #     x1, y1, x2, y2 = line[0]
        #     cv.line(color_frame, (x1, y1), (x2, y2), (0, 0, 255), 2)

        cv.imshow('color', color_frame)
        # cv.imshow('grayed', grayed_frame)
        # cv.imshow('binary', binary_frame)
        # cv.imshow('or', frame_or)
        # cv.imshow('result', result)
        # cv.imshow('hori', hori)
        # cv.imshow('verti', verti)
        # cv.imshow('sssss', morphed_frame)
        # cv.imshow('binary', binary_frame)
        if cv.waitKey(1) == 27:
            pipeline.stop()
            cv.destroyAllWindows()
            break
finally:
    pipeline.stop()