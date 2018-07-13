## This program is for DAC HDC contest ######
## 2017/11/22
## xxu8@nd.edu
## University of Notre Dame

import procfunc_ex as procfunc
import math
import numpy as np
import time
import ctypes
import cv2
#### !!!! you can import any package needed for your program ######

if __name__ == "__main__":
    
    teamName = 'SDU-LEGEND'
    DAC = '/home/nvidia/lsq-dac/test'

    resultRectangle = np.zeros((1, 4)) ## store all the results about tracking accuracy
    time_start=time.time()
    text = "%s:\n" % (time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    print(text)

    batchImageData = np.zeros((1, 360, 640, 3))
    img = cv2.imread("/home/nvidia/lsq-dac/data/4.jpg", 1)
    resized_img = cv2.resize(img, (640, 360)) 
    batchImageData[0,:,:] = resized_img[:,:]

    resultRectangle[0, :] = procfunc.detectionAndTracking(batchImageData, 1)
    print "here"           

    time_end = time.time()

    text = "%s:\n" % (time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    print(text)

    print resultRectangle


