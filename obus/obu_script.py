import paho.mqtt.client as mqtt
import time, json, multiprocessing as mp
from driving import *
from datetime import datetime

zone = [(37.87694, -25.78116), (37.87091, -25.77317),
        (37.8703, -25.78948), (37.86342, -25.78214)]

'''
points_to_discover = [(37.86991, -25.78726), (37.86856, -25.77842),
                        (37.87147, -25.78537), (37.87059, -25.77649),
                        (37.86961, -25.78198), (37.87496, -25.78142),
                        (37.86673, -25.78365), (37.86856, -25.78524),
                        (37.87249, -25.78284), (37.86656, -25.78073),
                        (37.87306, -25.78048), (37.87069, -25.77928)]
'''

def on_connect(client, userdata, flags, rc):
    if rc==0: 
        print("OBU"+str(client._client_id)[-2]+" connected")
    else: 
        print("bad connection code=",rc)
        
def on_publish(client,userdata,result):
    print("data published \n")
    
def on_disconnect(client, userdata, flags, rc=0):
    print("OBU"+str(client._client_id)[-2]+": disconnected")
    
def on_message(client, userdata, message):
  
    print("OBU"+str(client._client_id)[-2]+": message received")
    
def sendDENM(obu, point_discovered, obu_position):
    f = open('DENM.json')
    denm = json.load(f)
    denm['management']['actionID']['sequenceNumber'] += 1
    denm['situation']['eventType']['causeCode'] = point_discovered
    denm['detectionTime'] = datetime.timestamp(datetime.now())
    denm['referenceTime'] = datetime.timestamp(datetime.now())
    denm['management']['eventPosition']['latitude'] = obu_position[0]
    denm['management']['eventPosition']['longitude'] = obu_position[1]
    obu.publish("vanetza/in/denm", json.dumps(denm))    
    f.close()
    time.sleep(1)
    

def obu_process(broker, id, start_position):
    #print("OBU START POSITION {} FOR ID {} ".format(start_position, id))
    obu = mqtt.Client(client_id="obu"+str(id))
    obu.on_connect = on_connect
    obu.on_disconnect = on_disconnect
    
    obu.loop_start()
    obu.connect(broker)
    

    f = open('driving.json')    
    cam = json.load(f)
    cam['stationID'] = id+1

    obu_position = navigate_to_zone(start_position,zone, cam, obu)
    '''
    for destination_point in closests_points:
        obu_position  = navigate_to_point(obu_position,destination_point, cam, obu)
        causeCode = 1
        timer = 1
        frequency = 5
        sleep_time = 1 / frequency

        while timer > 0: 
            sendDENM(obu, causeCode, obu_position)
            time.sleep(sleep_time)
            timer -= sleep_time
        '''        
    obu.loop_stop()
    obu.disconnect()
    
def obu_init_simulation(broker_obus, start_point):
   
    process_list = []
    i = 0

    for broker in broker_obus:
        
        obuProcess = mp.Process(target=obu_process, args=[broker[0], broker[1], start_point])
        obuProcess.start()
        process_list.append(obuProcess)
        i += 1
        
    for obuProc in process_list:
        obuProc.join()    
        
if(__name__ == '__main__'):

    start_point = (37.86497, -25.78921)
    
    obu_init_simulation([("192.168.98.20",1),("192.168.98.30",2), ("192.168.98.40",3)], start_point)