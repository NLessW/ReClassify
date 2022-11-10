import cv2
# This is client code to receive video frames over UDP
import cv2, socket
import numpy as np
import base64
import paho.mqtt.client as mqtt #import the client1
import json
from matplotlib import pyplot as plt


class VideoCamera(object):
    
    
    def __init__(self, port, mIP, mPort, token):
        self.token = token
        self.client = mqtt.Client() #create new instance
        self.client.connect(mIP, port=mPort) #connect to broker
        self.BUFF_SIZE = 65536
        self.client_socket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        self.client_socket.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,self.BUFF_SIZE)
        self.client_socket.settimeout(3)
        self.host_name = socket.gethostname()
        self.port = port
        self.client_socket.bind(("0.0.0.0", self.port))
        msg,self.client_addr = self.client_socket.recvfrom(self.BUFF_SIZE)


    def __del__(self):
        self.video.release()   

    def __send_frame(self, data):
        topicLink = "free/"+self.token
        self.client.publish(topicLink, json.dumps(data))#publish

    def get_frame(self):
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
        packet,_ = self.client_socket.recvfrom(self.BUFF_SIZE)
        data = base64.b64decode(packet,' /')
        npdata = np.fromstring(data,dtype=np.uint8)
        frame = cv2.imdecode(npdata,1)
        
        # Object Detect
        classIds, confs, bbox = net.detect(frame, confThreshold=0.5)
        #print(classIds, bbox)
        r_dic = []
        if len(classIds) != 0:
            for classId, confidence,box in zip(classIds.flatten(),confs.flatten(),bbox):
                cv2.rectangle(frame,box,color=(0,255,0),thickness=2)
                cv2.putText(frame, c_Names[classId-1].upper(),(box[0]+10, box[1]+30),cv2.FONT_HERSHEY_COMPLEX,1,(0,255,0), 2)
                cv2.putText(frame, str(round(confidence*100,2)),(box[0]+200, box[1]+30),cv2.FONT_HERSHEY_COMPLEX,1,(0,255,0), 2)
                #print("Name : " + c_Names[classId-1]+"\n정확도 : " + str(round(confidence*100,2) ))
                x1=str(box[0])
                y1=str(box[1])
                x2=str(box[2])
                y2=str(box[3])
                r_locateR = {"x1" : x1, "y1" : y1, "x2" : x2, "y2" : y2}
                r_dicR = {"Name" : str(c_Names[classId-1]), "Acc" : str(round(confidence*100,2)) , "Locate" : r_locateR}
                r_dic.append(r_dicR)
                
             
        ret, jpeg = cv2.imencode('.jpg', frame)
        #with open('Detect_Data.json','w') as f:
            #json.dump(r_dic, f, indent=4)  
        
        data = r_dic
        self.__send_frame(data if data != None else {"data": "data"})
        return jpeg.tobytes()
