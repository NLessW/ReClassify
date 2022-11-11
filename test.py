import Reclassify as rc
from Reclassify import *

data=rc.mqttHandler

while(True):
    rc.feed(data)
    print(data)
