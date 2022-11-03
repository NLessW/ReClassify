import time
import cv2
import imutils
import platform
import numpy as np
from threading import Thread
from queue import Queue

class Streamer :
    
    def __init__(self ):
        
        if cv2.ocl.haveOpenCL() :
            cv2.ocl.setUseOpenCL(True)
        print('OpenCL : ', cv2.ocl.haveOpenCL())
            
        self.capture = None
        self.thread = None
        self.width = 640
        self.height = 360
        self.stat = False
        self.current_time = time.time()
        self.preview_time = time.time()
        self.sec = 0
        self.Q = Queue(maxsize=128)
        self.started = False
        
        
    def run(self, src = 0 ) :
        
        self.stop()
        
        if platform.system() == 'Windows' :        
            self.capture = cv2.VideoCapture( src , cv2.CAP_DSHOW )
        
        else :
            self.capture = cv2.VideoCapture( src )
            
        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        
        if self.thread is None :
            self.thread = Thread(target=self.update, args=())
            self.thread.daemon = False
            self.thread.start()
        
        self.started = True

    def stop(self):
        
        self.started = False
        
        if self.capture is not None :
            
            self.capture.release()
            self.clear()
            
    def update(self):
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
            if self.started :
                rt, img = self.capture.read()
                sucess,img2 = self.capture.read()
                
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
                #cv2.imshow("result",img_hor)
                #cv2.waitKey(1)
                
                if sucess : 
                    self.Q.put(img_hor)
    def clear(self):
        
        with self.Q.mutex:
            self.Q.queue.clear()
            
    def read(self):

        return self.Q.get()

    def blank(self):
        
        return np.ones(shape=[self.height, self.width, 3], dtype=np.uint8)
    
    def bytescode(self):
        
        if not self.capture.isOpened():
            
            img2 = self.blank()

        else :
            
            img2 = imutils.resize(self.read(), width=int(self.width) )
        
            if self.stat :  
                cv2.rectangle( img2, (0,0), (120,30), (0,0,0), -1)
                fps = 'FPS : ' + str(self.fps())
                cv2.putText  ( img2, fps, (10,20), cv2.FONT_HERSHEY_PLAIN, 1, (0,0,255), 1, cv2.LINE_AA)
            
            
        return cv2.imencode('.jpg', img2 )[1].tobytes()
    
    def fps(self):
        
        self.current_time = time.time()
        self.sec = self.current_time - self.preview_time
        self.preview_time = self.current_time
        
        if self.sec > 0 :
            fps = round(1/(self.sec),1)
            
        else :
            fps = 1
            
        return fps
                   
    def __exit__(self) :
        print( '* streamer class exit')
        self.capture.release()
