import base64
import cv2 as cv
import numpy as np
import paho.mqtt.client as mqtt

MQTT_BROKER = "sshmein.ekstrah.com"
MQTT_RECEIVE = "frame/token/test"
MQTT_RECEIVE_L = 'frame/token/testl'

frame = np.zeros((240, 320, 3), np.uint8)

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe(MQTT_RECEIVE)


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    global frame
    # Decoding the message
    img = base64.b64decode(msg.payload)
    # converting into numpy array from buffer
    npimg = np.frombuffer(img, dtype=np.uint8)
    # Decode to Original Frame
    frame = cv.imdecode(npimg, 1)


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(MQTT_BROKER, 9881)

# Starting thread which will receive the frames
client.loop_start()

while True:
    # cv.imshow("Stream", frame)
    _, buffer = cv.imencode('.jpg', frame)
    # Converting into encoded bytes
    jpg_as_text = base64.b64encode(buffer)
    # Publishig the Frame on the Topic home/server
    client.publish(MQTT_RECEIVE_L, jpg_as_text)
    # if cv.waitKey(1) & 0xFF == ord('q'):
    #     break

# Stop the Thread
client.loop_stop()
