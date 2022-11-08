import cv2
# This is client code to receive video frames over UDP
import cv2, socket
import numpy as np
import base64
import paho.mqtt.client as mqtt #import the client1
import json

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
        packet,_ = self.client_socket.recvfrom(self.BUFF_SIZE)
        data = base64.b64decode(packet,' /')
        npdata = np.fromstring(data,dtype=np.uint8)
        frame = cv2.imdecode(npdata,1)
        # DO WHAT YOU WANT WITH TENSORFLOW / KERAS AND OPENCV
        ret, jpeg = cv2.imencode('.jpg', frame)
        data = None #Data is information about classification in json form or dict
        self.__send_frame(data if data != None else {"data": "data"})
        return jpeg.tobytes()