import ReClassify.ReClassify as rc
import json

def customMessage(mqttc, obj, msg):
    data = json.loads(msg.payload.decode('utf-8'))
    print(data)
client = rc(customMessage)
client.go()
