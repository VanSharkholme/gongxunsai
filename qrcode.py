import cv2 as cv
from pyzbar import pyzbar

def qrcode_recognition(img):
    msgs = pyzbar.decode(img)
    ret_data = []
    for msg in msgs:
        (x, y, w, h) = msg.rect
        cv.rectangle(img, (x,y), (x+w, y+h), (0,0,255), 2)
        data = msg.data.decode("utf-8")
        ret_data.append(data)
        print(data)
        cv.putText(img, data, (x,y - 10), cv.FONT_HERSHEY_COMPLEX, 0.5, (0,0,255), 2)
    return ret_data

def set_camera_properties(capture):
    capture.set(cv.CAP_PROP_FRAME_WIDTH, 960)
    capture.set(cv.CAP_PROP_FRAME_HEIGHT, 540)
    capture.set(cv.CAP_PROP_FPS, 30)
    # capture.set(cv.CAP_PROP_BRIGHTNESS, -100)
    # capture.set(cv.CAP_PROP_CONTRAST,40)
    # capture.set(cv.CAP_PROP_SATURATION, 50)
    # capture.set(cv.CAP_PROP_HUE, 50)
    # capture.set(cv.CAP_PROP_EXPOSURE, 50)


cap = cv.VideoCapture(0)

print(cap.get(cv.CAP_PROP_BRIGHTNESS))
set_camera_properties(cap)
# size = (int(cap.get(cv.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv.CAP_PROP_FRAME_HEIGHT)))
while True:
    ret, frame = cap.read()
    grayed = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    threshold = cv.adaptiveThreshold(grayed, 255, cv.ADAPTIVE_THRESH_MEAN_C, cv.THRESH_BINARY, 27, 10)

    # tmp = qrcode_recognition(frame)
    msgs = pyzbar.decode(threshold)
    for msg in msgs:
        (x, y, w, h) = msg.rect
        cv.rectangle(frame, (x,y), (x+w, y+h), (0,0,255), 2)
        data = msg.data.decode("utf-8")
        # ret_data.append(data)
        print(data)
        cv.putText(frame, data, (x,y - 10), cv.FONT_HERSHEY_COMPLEX, 0.5, (0,0,255), 2)

    cv.imshow("camera",frame)
    if cv.waitKey(1) == 27:
        break


cap.release()



