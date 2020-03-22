import paho.mqtt.client as mqtt
import logging, sys
import json
import time
from my_sip_caller import toCall
import threading
import multiprocessing

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
hdlr = logging.StreamHandler(sys.stdout)
logger.addHandler(hdlr)

MQTT_CLIENT_ID = 'Client1'
MQTT_USER = 'mqttuser'
MQTT_PASSWORD = 'mqttpassword'
# MQTT_TOPIC = 'topic_pokus'
MQTT_TOPIC = 'zigbee2mqtt/0x00158d0003cbcc25'
MQTT_ADDRESS = 'localhost'

START_TIME = 0
END_TIME = 0

# class callThread(threading.Thread):
#     def run(self):
#         toCall()
def callproc():
    toCall()
    
def writeMesg(topic, payload, START_TIME):
    with open("output.txt", 'a+') as f:
        f.write("%s : %s\n" %(topic, payload))
        res = json.loads(payload)
        # print(res["occupancy"])
        logger.info(res["occupancy"])
        END_TIME = time.time()
        logger.info("Time elapsed: %f" %(END_TIME - START_TIME))
        
        
def on_connect(client, userdata, flags, rc):
    """ The callback for when the client receives a CONNACK response from the server."""
    print('Connected with result code ' + str(rc))
    client.subscribe(MQTT_TOPIC)
        
def on_message(client, userdata, message):
    START_TIME = time.time()
#     writeMesg(message.topic, message.payload.decode('utf-8'), START_TIME)
#     print(message.topic)
#     print(message.payload)
#     my_sip_caller.toCall()
#     print("msg received")
    p = multiprocessing.Process(target=callproc)
    p.start()
    p.join(10)
    
def main():
    my_mqtt_client = mqtt.Client(MQTT_CLIENT_ID)
    my_mqtt_client.on_connect = on_connect
    my_mqtt_client.on_message = on_message
    
    my_mqtt_client.connect(MQTT_ADDRESS, 1883)
    my_mqtt_client.loop_forever()
    
if __name__ == "__main__":
    main()
    