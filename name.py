import os
# import pyrealsense2 as rs
#
# print(rs.__path__)

path = 'pic/target1/'
f = os.listdir(path)
n = 422
for i in f:
    newname = str(n)+'.jpg'
    os.rename(path+i, 'targets_orig_data/'+newname)
    n += 1
print('done')
