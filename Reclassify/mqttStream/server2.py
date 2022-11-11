from flask import Flask, render_template, Response
from flask_mqtt import Mqtt
import base64
import cv2 as cv
import numpy as np


frame = np.zeros((240, 320, 3), np.uint8)

app = Flask(__name__)
app.config['MQTT_BROKER_URL'] = '127.0.0.1'  # use the free broker from HIVEMQ
app.config['MQTT_BROKER_PORT'] = 9881  # default port for non-tls connection
app.config['MQTT_KEEPALIVE'] = 5  # set the time interval for sending a ping to the broker to 5 seconds

mqtt = Mqtt()

@mqtt.on_connect()
def handle_connect(client, userdata, flags, rc):
    if rc == 0:
       print('Connected successfully')
       mqtt.subscribe('home/server')
    else:
       print('Bad connection. Code:', rc)

@mqtt.on_message()
def handle_mqtt_message(client, userdata, message):
    global frame
    # Decoding the message
    img = base64.b64decode(message.payload)
    # converting into numpy array from buffer
    npimg = np.frombuffer(img, dtype=np.uint8)
    # Decode to Original Frame
    frame = cv.imdecode(npimg, 1)
    ret, jpeg = cv.imencode('.jpg', frame)
    print(frame)
    frame = jpeg


@app.route('/')
def index():
    return render_template('index.html')

def gen():
    while True:
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(gen(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    app.run(debug=True)