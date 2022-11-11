import cv2, imutils, socket
import base64
import threading
import paho.mqtt.client as mqtt
import json


class ReClassify(object):
    data = {}
    def __init__(self, on_messageFunction):
        self.mqttc = mqtt.Client()
        self.mqttc.on_message = on_messageFunction
        self.mqttc.on_connect = self.on_connect
        self.mqttc.on_publish = self.on_publish
        self.mqttc.on_subscribe = self.on_subscribe
        self.mqttc.connect("127.0.0.1", 9881, 60)
        self.mqttc.subscribe("#", 0) # That symbole will be replaced with token
        pass

    def on_connect(self, mqttc, obj, flags, rc):
        print("rc: " + str(rc))



    def on_publish(self, mqttc, obj, mid):
        print("mid: " + str(mid))

    def on_subscribe(self, mqttc, obj, mid, granted_qos):
        print("Subscribed: " + str(mid) + " " + str(granted_qos))

    def on_log(self, mqttc, obj, level, string):
        print(string)

    def go(self):
        self.mqttc.loop_forever()