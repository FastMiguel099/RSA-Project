import json
import paho.mqtt.client as mqtt
import threading
from time import sleep
from os import getenv
from geopy.distance import geodesic

def genCenters(x_min, y_min, x_max, y_max, precision):
    side = (x_max-x_min) / precision
    
    x_vals = []
    y_vals = []
    vals = []
    for x in range(10):
        if x==0:
            x_vals.append(x_min + side/2)
            continue
        x_vals.append(x_vals[-1] + side)

    for x in range(10):
        if x==0:
            y_vals.append(y_min + side/2)
            continue
        y_vals.append(y_vals[-1] + side)

    for x in x_vals:
        for y in y_vals:
            vals.append(( round(x, 5), round(y, 5) ))
    return vals

def calculate_closest(curr, zone):
    return min(zone, key=lambda point: geodesic(curr, point).m)    

def gen_coords(start, end, step):
    x_displacement = round(end[0] - start[0],5)
    y_displacement = round(end[1] - start[1],5)
    # print("Moving", x_displacement, "in x axis and", y_displacement, "in y axis" )
    x_step = x_displacement/step
    y_step = y_displacement/step
    crds = []
    new_x = start[0]
    new_y = start[1]

    #does not include starting position coordinates
    for i in range (step):
        new_x += x_step
        new_y += y_step
        crds.append((new_x, new_y))

    #print(crds)
    return crds

def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe("vanetza/out/denm")
    # should also subscribe to CAMs

# É chamada automaticamente sempre que recebe uma mensagem nos tópicos subscritos em cima
def on_message(client, userdata, msg):
    print("\n\nUnknown topic: " + msg.topic)
    print(msg.payload.decode('utf-8'), "\n\n")
    return
    message = json.loads(msg.payload.decode('utf-8'))
    
    print("\n\nTopic: " + msg.topic)
    print("From:", message["management"]["actionID"]["originatingStationID"])
    lat = message["management"]["eventPosition"]["latitude"]
    lon = message["management"]["eventPosition"]["longitude"]
    print("Location:", lat, ";", lon, "\n\n")
    

    # lat = message["latitude"]
    # ...

def ganzarina(client, userdate, msg):
    # message = json.loads(msg.payload.decode('utf-8'))
    # lat = message["management"]["eventPosition"]["latitude"]
    # lon = message["management"]["eventPosition"]["longitude"]
    print("\n\nGanzarina:")
    #print("Location:", lat, ";", lon, "\n\n")

# publish
def generate(_boat_id):
    if _boat_id!=1:
        #print("nothing here")
        sleep(1)
        return
    f = open('in_denm.json')
    m = json.load(f)
    m["management"]["actionID"]["originatingStationID"] = _boat_id
    # m["latitude"] = 0
    # m["longitude"] = 0
    m = json.dumps(m)
    client.publish("vanetza/in/denm",m)
    print("published->")
    f.close()
    sleep(3)

# coordinates init
zone = [(37.87400, -25.78800), (37.87400, -25.77800), (37.8640, -25.77800), (37.86400, -25.78800)]
min_tuple = min(zone, key=lambda tup: tup[1]+tup[0])
max_tuple = max(zone, key=lambda tup: tup[1]+tup[0])
cntrs = genCenters(min_tuple[1], min_tuple[0], max_tuple[1], max_tuple[0], 10)

#publica no in e recebe no out

# env init
boat_id = int(getenv('BOAT_ID'))
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.message_callback_add("vanetza/out/denm", ganzarina)
client.connect(getenv('BROKER_IP'), 1883, 60)

# coms init 
start_point = cntrs[0]  # this var should come from docker-compose, maybe step var should too
# send denm with current point
curr_point = start_point
print(cntrs)
print(curr_point)
cntrs.remove(start_point)

# computing init
sleep(5)
print("Starting loop...")
threading.Thread(target=client.loop_forever).start()

# looped task
while(True):
    # dict = [591, 1281, 12881, 1985]
    # for a in dict:
    #     print(a)
    closest = calculate_closest(curr_point, zone)
    mov_coords = gen_coords(curr_point, closest, 5)
    generate(boat_id)
    sleep(1)



#start location, send message that discovered square, update sequence nº
#move to first square
#send message that discovered square, update sequence nº
#calculate closest square
#move to next closest square



# broker = "172.19.0.2/16"
# port = 1883
# topic = "mytopic"

# def on_message(client, userdata, message):
#     print(f"Received: {message.payload.decode()}")


# client = mqtt.Client()
# #client.on_message = on_message
# print("hello")
# #client.connect(broker, port)
# #client.subscribe(topic)
#client.loop_forever()


