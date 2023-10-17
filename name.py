import os
# import pyrealsense2 as rs
#
# print(rs.__path__)

path = 'datasets/combined_dataset/labels_t/'
f = os.listdir(path)
n = 835
for i in f:
    newname = str(n)+'.txt'
    os.rename(path+i, path+newname)
    n += 1
print('done')
