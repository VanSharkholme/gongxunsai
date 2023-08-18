import cv2 as cv
import numpy as np

# img = cv.imread("pic1.jpg")
# assert img is not None, "picture open failed"

# print(img)

# print(img[0, 0])
# for i in range(0,512, 2):
#     for j in range(0, 512, 2):
#         img[i, j] = [255, 255, 255]

# wife = img[0:512, 200:450]
# border = cv.copyMakeBorder(img, 10, 10, 10, 10, cv.BORDER_CONSTANT, value=[255, 255, 255])
# imgray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
# ret, threshold = cv.threshold(imgray, 100, 250, 0)
# contours, hierarchy = cv.findContours(threshold, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
# edged = cv.Canny(img, 100, 400)
# cv.drawContours(img, contours, -1, (255,0,0), 1)
# cv.imshow("pic1", threshold)

# cv.waitKey()
# print(img.dtype)

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

# coder = cv.QRCodeDetector()

while True:
    ret, frame = cap.read()
    grayed = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)

    # gradX = cv.Sobel(grayed, cv.CV_32F, 1, 0, -1)
    # gradY = cv.Sobel(grayed, cv.CV_32F, 0, 1, -1)

    # gradient = cv.subtract(gradX, gradY)
    # gradient = cv.convertScaleAbs(gradient)

    # blurred = cv.blur(gradient, (9, 9))
    # (_, thresh) = cv.threshold(blurred, 160, 160, cv.THRESH_BINARY)

    # kernel = cv.getStructuringElement(cv.MORPH_RECT, (21, 7))
    # closed = cv.morphologyEx(thresh, cv.MORPH_CLOSE, kernel)

    # closed = cv.erode(closed, None, iterations = 4)
    # closed = cv.dilate(closed, None, iterations = 4)

    # contour,hierarchy = cv.findContours(closed.copy(), cv.RETR_EXTERNAL,cv.CHAIN_APPROX_SIMPLE)

    # c = sorted(cnts, key = cv.contourArea, reverse = True)[0]
    # rect = cv.minAreaRect(c)
    # box = np.int0(cv.boxPoints(rect))

    # ret_t, threshold = cv.threshold(grayed, 170, 900, 0)
    threshold = cv.adaptiveThreshold(grayed, 255, cv.ADAPTIVE_THRESH_MEAN_C, cv.THRESH_BINARY, 27, 10)

    # tmp = qrcode_recognition(frame)
    # msgs = pyzbar.decode(frame)
    # for msg in msgs:
    #     (x, y, w, h) = msg.rect
    #     cv.rectangle(frame, (x,y), (x+w, y+h), (0,0,255), 2)
    #     data = msg.data.decode("utf-8")
    #     # ret_data.append(data)
    #     print(data)
    #     cv.putText(frame, data, (x,y - 10), cv.FONT_HERSHEY_COMPLEX, 0.5, (0,0,255), 2)

    # cv.drawContours(frame,contour,-1,(0,0,255),3) 
    cv.imshow("camera", threshold)
    if cv.waitKey(1) == 27:
        break


cap.release()



