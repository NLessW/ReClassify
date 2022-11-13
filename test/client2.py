# This is server code to send video frames over UDP
import cv2, imutils, socket
import base64
import threading
import paho.mqtt.client as mqtt
import argparse





def videoSending(porty):
	BUFF_SIZE = 65536
	server_socket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
	server_socket.setsockopt(socket.SOL_SOCKET,socket.SO_RCVBUF,BUFF_SIZE)
	host_ip = 'sshmein.ekstrah.com'#  socket.gethostbyname(host_name)
	print(host_ip)
	port = porty
	socket_address = (host_ip,port)
	message = b'hello'
	server_socket.sendto(message,(host_ip,port))
	print('Sending it to:',socket_address)

	vid = cv2.VideoCapture(0) #  replace 'rocket.mp4' with 0 for webcam
	fps,st,frames_to_count,cnt = (0,0,20,0)

	while True:
		print('Sending data to ', socket_address)
		WIDTH=400
		while(vid.isOpened()):
			_,frame = vid.read()
			frame = imutils.resize(frame,width=WIDTH)
			encoded,buffer = cv2.imencode('.jpg',frame,[cv2.IMWRITE_JPEG_QUALITY,80])
			message = base64.b64encode(buffer)
			server_socket.sendto(message,socket_address)
			frame = cv2.putText(frame,'FPS: '+str(fps),(10,40),cv2.FONT_HERSHEY_SIMPLEX,0.7,(0,0,255),2)



def on_connect(mqttc, obj, flags, rc):
    print("rc: " + str(rc))

def on_message(mqttc, obj, msg):
    print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))
    print("message")

def on_publish(mqttc, obj, mid):
    print("mid: " + str(mid))

def on_subscribe(mqttc, obj, mid, granted_qos):
    print("Subscribed: " + str(mid) + " " + str(granted_qos))

def on_log(mqttc, obj, level, string):
    print(string)

def mqttHandler():
	mqttc = mqtt.Client()
	mqttc.on_message = on_message
	mqttc.on_connect = on_connect
	mqttc.on_publish = on_publish
	mqttc.on_subscribe = on_subscribe
	mqttc.connect("sshmein.ekstrah.com", 9881, 60)
	mqttc.subscribe("#", 0) # That symbole will be replaced with token

	mqttc.loop_forever()

if __name__ == "__main__":
	
	parser = argparse.ArgumentParser()
	parser.add_argument("--port", type=int)
	args = parser.parse_args()
	porty = args.port
	t1 = threading.Thread(target=videoSending, args=(porty))
	t2 = threading.Thread(target=mqttHandler)
	t1.start()
	t2.start()