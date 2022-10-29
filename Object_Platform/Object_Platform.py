import cv2
import numpy as np
from matplotlib import pyplot as plt

cap = cv2.VideoCapture(0)
cap.set(3,640)
cap.set(4,480)


c_Names = []
c_File = 'coco.names'
with open(c_File,'rt') as f:
    c_Names = f.read().rstrip('\n').split('\n')

confPath = 'ssd_mobilenet_v3_large_coco_2020_01_14.pbtxt'
weiPath = 'frozen_inference_graph.pb'

net = cv2.dnn_DetectionModel(weiPath, confPath)
net.setInputSize(320,320)
net.setInputScale(1.0/ 127.5)
net.setInputMean((127.5, 127.5, 127.5))
net.setInputSwapRB(True)


while True:
    rt, img = cap.read()
    sucess,img2 = cap.read()
    
    classIds, confs, bbox = net.detect(img2, confThreshold=0.5)
    print(classIds, bbox)
    if len(classIds) != 0:
        for classId, confidence,box in zip(classIds.flatten(),confs.flatten(),bbox):
            cv2.rectangle(img2,box,color=(0,255,0),thickness=2)
            cv2.putText(img2, c_Names[classId-1].upper(),(box[0]+10, box[1]+30),cv2.FONT_HERSHEY_COMPLEX,1,(0,255,0), 2)
            cv2.putText(img2, str(round(confidence*100,2)),(box[0]+200, box[1]+30),cv2.FONT_HERSHEY_COMPLEX,1,(0,255,0), 2)
            print("이름 : " + c_Names[classId-1]+"\n정확도 : " + str(round(confidence*100,2) ))
    img_hor =  np.hstack((img,img2))
    #cv2.imshow("Input", img)
    #cv2.imshow("Output",img2)
    cv2.imshow("result",img_hor)
    cv2.waitKey(1)
