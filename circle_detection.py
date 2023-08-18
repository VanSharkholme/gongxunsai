import cv2 as cv
import numpy as np

import cv2
import numpy as np

# 大津二值化算法
def otsu(gray_img):
    h = gray_img.shape[0]
    w = gray_img.shape[1]

    threshold_t = 0
    max_g =0

    # 遍历每一个灰度层
    for t in range(255):
        # 使用numpy直接对数组进行运算
        n0 = gray_img[np.where(gray_img <t)]
        n1 = gray_img[np.where(gray_img >=t)]

        w0 = len(n0)/(h*w)
        w1 = len(n1)/(h*w)

        u0 = np.mean(n0) if len(n0) >0 else 0.
        u1 = np.mean(n1) if len(n1) >0 else 0.

        g = w0*w1*(u0-u1)**2
        if g>max_g:
            max_g=g
            threshold_t = t

    print('类间最大方差的阈值：',threshold_t)
    gray_img[gray_img < threshold_t] = 0
    gray_img[gray_img >= threshold_t] =255
    return gray_img

def draw_contour(contours):
    if len(contours) != 0:
        min_area = 5
        target = contours[0]
        for contour in contours:
            area = cv.contourArea(contour)
            if area > min_area:
                min_area = area
                target = contour
    # rimg = 
    # cimg = cv.cvtColor(img,cv.COLOR_GRAY2BGR)
        if len(target) > 5:
            center, axes, angle = cv.fitEllipse(target)
            center = (int(center[0]), int(center[1]))
            axes = (int(axes[0]), int(axes[1]))
            # print(center, axes, angle)
            cv.drawContours(frame, target, -1, (255,255,255), 3)
            cv.circle(frame, center, 3, (0,255,0), -1)















def set_camera_properties(capture):
    capture.set(cv.CAP_PROP_FRAME_WIDTH, 960)
    capture.set(cv.CAP_PROP_FRAME_HEIGHT, 540)
    capture.set(cv.CAP_PROP_FPS, 30)
    # capture.set(cv.CAP_PROP_BRIGHTNESS, 1)
    # capture.set(cv.CAP_PROP_CONTRAST,40)
    # capture.set(cv.CAP_PROP_SATURATION, 50)
# capture.set(cv.CAP_PROP_HUE, 50)
    # capture.set(cv.CAP_PROP_EXPOSURE, 50)

cap = cv.VideoCapture(0)
set_camera_properties(cap)
# pic_path = "circles.jpg"
# circle_img_org = cv.imread(pic_path)
# assert circle_img_org is not None, "picture open failed"

# img = circle_img_org

while True:
    ret, frame = cap.read()
    frame_contour = frame.copy()
    # img = cv.resize(frame, None, fx=0.4, fy=0.4)
    # result = cv.resize(circle_img_org, None, fx=0.2, fy=0.2)
    # 降低画面亮度
    lookUpTable = np.empty((1,256), np.uint8)
    for i in range(256):
        lookUpTable[0,i] = np.clip(pow(i / 255.0, 1.5) * 255.0, 0, 255) #pow内第二个参数为gamma
    dark = cv.LUT(frame, lookUpTable)

    # 提取蓝色通道
    blur = cv.medianBlur(dark,5)
    hsv = cv.cvtColor(blur, cv.COLOR_BGR2HSV)
    img = cv.cvtColor(blur, cv.COLOR_BGR2GRAY)

    lower_blue = np.array([105, 45, 45])
    upper_blue = np.array([135, 255, 255])

    lower_red = np.array([170, 45, 45])
    upper_red = np.array([10, 255, 255])

    lower_green = np.array([50, 45, 45])
    upper_green = np.array([70, 255, 255])


    mask_blue = cv.inRange(hsv, lower_blue, upper_blue)
    mask_red = cv.inRange(hsv, lower_red, upper_red)
    mask_green = cv.inRange(hsv, lower_green, upper_green)

    blue_channel = cv.bitwise_and(frame, frame, mask=mask_blue)
    red_channel = cv.bitwise_and(frame, frame, mask=mask_red)
    green_channel = cv.bitwise_and(frame, frame, mask=mask_green)

    grayed_blue = cv.cvtColor(blue_channel, cv.COLOR_BGR2GRAY)
    ret_b, threshold_b = cv.threshold(grayed_blue, 45, 255, cv.THRESH_BINARY)

    grayed_red = cv.cvtColor(red_channel, cv.COLOR_BGR2GRAY)
    ret_r, threshold_r = cv.threshold(grayed_red, 45, 255, cv.THRESH_BINARY)

    grayed_green = cv.cvtColor(green_channel, cv.COLOR_BGR2GRAY)
    ret_g, threshold_g = cv.threshold(grayed_green, 45, 255, cv.THRESH_BINARY)

    contours_b, hierarchy_b = cv.findContours(threshold_b, cv.RETR_TREE,cv.CHAIN_APPROX_SIMPLE)
    contours_r, hierarchy_r = cv.findContours(threshold_r, cv.RETR_TREE,cv.CHAIN_APPROX_SIMPLE)
    contours_g, hierarchy_g = cv.findContours(threshold_g, cv.RETR_TREE,cv.CHAIN_APPROX_SIMPLE)

    draw_contour(contours_b)
    # draw_contour(contours_g)
    # draw_contour(contours_r)


            # cv.ellipse(frame, center, axes, angle, 0, 360, color=(255,255,255), thickness=3)
    cv.imshow('camera', blue_channel)
    # cv.imshow('contour', frame_contour)

    if cv.waitKey(1) == 27:
        break


cap.release()


# filter = cv.pyrMeanShiftFiltering(circle_img_org, 10, 100)
# cv.GaussianBlur()
# circles = cv.HoughCircles(grayed, cv.HOUGH_GRADIENT, 1, 20, param1=100, param2=50, minRadius=0, maxRadius=0)

# # print(type(circles[0][0][0]))


# for circle in circles[0]:
#     pass
#     # print(circle[0])
#     x,y,r = map(int, circle)
#     print(circle)
#     cv.circle(result, (x,y), r, (0,0,255), 2)
#     cv.circle(result, (x,y), 2, (255,0,0), 4)

# cv.imshow("img", result)
# # cv.resizeWindow("img", 800, 600)
# cv.waitKey()


    # cv.imshow("camera",threshold)