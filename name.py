import os
# import pyrealsense2 as rs
#
# print(rs.__path__)

path = 'pic/intel1.mp4/'
f = os.listdir(path)
n = 817
for i in f:
    newname = str(n)+'.jpg'
    os.rename(path+i, 'clear_pic/'+newname)
    n += 1
