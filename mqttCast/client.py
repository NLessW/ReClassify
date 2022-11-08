# Importing Libraries
import cv2 as cv
import paho.mqtt.client as mqtt
import base64
import time
import numpy as np

frameR = np.zeros((240, 320, 3), np.uint8)

def on_message(client, userdata, msg):
    global frameR
    # Decoding the message
    img = base64.b64decode(msg.payload)
    # converting into numpy array from buffer
    npimg = np.frombuffer(img, dtype=np.uint8)
    # Decode to Original Frame
    frameR = cv.imdecode(npimg, 1)

MQTT_BROKER = "sshmein.ekstrah.com"
MQTT_SEND = "frame/token/test"
MQTT_RECEIVE = 'frame/token/testl'
cap = cv.VideoCapture(0)
client = mqtt.Client()
client.connect(MQTT_BROKER, 9881)
client.on_message=on_message
client.loop_start()
try:
    while True:
        start = time.time()
        # Read Frame
        _, frame = cap.read()
        # Encoding the Frame
        _, buffer = cv.imencode('.jpg', frame)
        # Converting into encoded bytes
        jpg_as_text = base64.b64encode(buffer)
        # Publishig the Frame on the Topic home/server
        client.publish(MQTT_SEND, jpg_as_text)
        end = time.time()
        t = end - start
        fps = 1/t
        print(fps)
        client.subscribe(MQTT_RECEIVE)
        cv.imshow('stream', frameR)
        if cv.waitKey(1) & 0xFF == ord('q'):
            break
except:
    cap.release()
    client.disconnect()
    client.loop_stop()
    print("\nNow you can restart fresh")
