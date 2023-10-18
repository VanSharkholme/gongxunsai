import cv2 as cv
from realsense_start import *
from pyzbar import pyzbar
import sys
from serial_screen import *

def qrcode_recognition(img):
    msgs = pyzbar.decode(img)
    ret_data = []
    for msg in msgs:
        (x, y, w, h) = msg.rect
        cv.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 2)
        data = msg.data.decode("utf-8")
        ret_data.append(data)
        print(data)
        # cv.putText(img, data, (x, y - 10), cv.FONT_HERSHEY_COMPLEX, 0.5, (0, 0, 255), 2)
    return ret_data


# def set_camera_properties(capture):
#     capture.set(cv.CAP_PROP_FRAME_WIDTH, 960)
#     capture.set(cv.CAP_PROP_FRAME_HEIGHT, 540)
#     capture.set(cv.CAP_PROP_FPS, 30)
#     # capture.set(cv.CAP_PROP_BRIGHTNESS, -100)
#     # capture.set(cv.CAP_PROP_CONTRAST,40)
#     # capture.set(cv.CAP_PROP_SATURATION, 50)
#     # capture.set(cv.CAP_PROP_HUE, 50)
#     # capture.set(cv.CAP_PROP_EXPOSURE, 50)


# cap = cv.VideoCapture(0, cv.CAP_V4L2)
#
# print(cap.get(cv.CAP_PROP_BRIGHTNESS))
# set_camera_properties(cap)
# size = (int(cap.get(cv.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv.CAP_PROP_FRAME_HEIGHT)))
def qr_scan(cam) -> str:
    # cam = realsense_cam((1280, 720), 30)
    try:
        while True:
            # ret, frame = cap.read()
            frames = cam.get_frames()
            frame = frames['color']
            grayed = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
            threshold = cv.adaptiveThreshold(grayed, 255, cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_BINARY, 27, 2)
            threshold = cv.morphologyEx(threshold, cv.MORPH_CLOSE, (3, 3))
            # tmp = qrcode_recognition(frame)
            msgs = pyzbar.decode(grayed)
            if msgs:
            # (x, y, w, h) = msg.rect
            # cv.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
                data = msgs[0].data.decode("utf-8")
                # ret_data.append(data)
                print(data)
                send_serial(data)
                break

                # cv.putText(frame, data, (x, y - 10), cv.FONT_HERSHEY_COMPLEX, 0.5, (0, 0, 255), 2)

            # cv.imshow("camera", frame)
            # if cv.waitKey(1) == 27:
            #     cv.destroyAllWindows()
            #     break

    finally:
        return data
        # sys.exit()


if __name__ == '__main__':
    qr_scan()
