import cv2 as cv
import time
import os


# def set_camera_properties(capture):
#     capture.set(cv.CAP_PROP_FRAME_WIDTH, 960)
#     capture.set(cv.CAP_PROP_FRAME_HEIGHT, 540)
#     capture.set(cv.CAP_PROP_FPS, 30)
#     # capture.set(cv.CAP_PROP_BRIGHTNESS, 1)
#     # capture.set(cv.CAP_PROP_CONTRAST,40)
#     # capture.set(cv.CAP_PROP_SATURATION, 50)
# # capture.set(cv.CAP_PROP_HUE, 50)
#     # capture.set(cv.CAP_PROP_EXPOSURE, 50)


# cap = cv.VideoCapture(0)
# set_camera_properties(cap)
# cnt = 0
# time.sleep(2)
# last_time = time.time()
# while True:
#     ret, frame = cap.read()
#     cv.imshow('camera',frame)
#     new_time = time.time()
#     if new_time - last_time >= 1:
#         cv.imwrite('pic/'+str(cnt)+'.jpg', frame)
#         last_time = new_time
#         cnt += 1
#     if cv.waitKey(1) == 27:
#         break

def video_split(video_path, save_path):
    '''
	对视频文件切割成帧
	'''
    '''
	@param video_path:视频路径
	@param save_path:保存切分后帧的路径
	'''
    vc = cv.VideoCapture(video_path)
    # 一帧一帧的分割 需要几帧写几
    c = 0
    if vc.isOpened():
        rval, frame = vc.read()
    else:
        rval = False
    while rval:
        rval, frame = vc.read()
        # 每秒提取5帧图片
        if c % 10 == 0:
            cv.imwrite(save_path + "/" + str('%06d' % c) + '.jpg', frame)
            cv.waitKey(1)
        c = c + 1


# f = os.listdir('raw_videos/')
# print(f)
# for i in f:
video_split('raw_videos/intel1.mp4', 'pic/intel1.mp4')
# video_split('video.mp4','pic')
