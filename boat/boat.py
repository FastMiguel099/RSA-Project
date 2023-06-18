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

def calculate_closest(curr, centers):
    return min(centers, key=lambda point: geodesic(curr, point).m)    

def gen_coords(start, end, step):
    if step==0:
        print("Processing starting point")
        return [end]
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
        
        crds.append((round(new_x,5), round(new_y,5)))

    return crds

def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe("vanetza/out/denm")
    # should also subscribe to CAMs


def on_message(client, userdata, msg):
    print("\n\nUnknown topic: " + msg.topic)
    print(msg.payload.decode('utf-8'), "\n\n")
    return


def foreign_discovery(client, userdate, msg):
    message = json.loads(msg.payload.decode('utf-8'))
    lat = message['fields']['denm']["management"]["eventPosition"]["latitude"]
    lon = message['fields']['denm']["management"]["eventPosition"]["longitude"]
    foreign_point = (lon, lat)
    # print("\nForeign discovery:", foreign_point)
    global closest, stop_loop

    if not closest:
        closest=eval(getenv('START_POINT'))
    if foreign_point==closest:
        print("My current destination has already been discovered !")
        if foreign_point in cntrs:
            cntrs.remove(foreign_point)
        stop_loop = True
        return
    if foreign_point in cntrs:
        cntrs.remove(foreign_point)
        if not cntrs:
            print("NOT CNTRS must stop (foreign)")
            stop_loop = True


def publish_discovery(point):
    global sqnc_no
    f = open('in_denm.json')
    m = json.load(f)
    m["management"]["actionID"]["originatingStationID"] = boat_id
    m["management"]["actionID"]["sequenceNumber"] = sqnc_no
    #detection time?
    #reference time?
    m["management"]["eventPosition"]["latitude"] = point[1]
    m["management"]["eventPosition"]["longitude"] = point[0]
    m = json.dumps(m)

    if point in cntrs:
        cntrs.remove(point)
        sqnc_no += 1

    client.publish("vanetza/in/denm",m)
    print("published discovery", point)


def publish_movement(coords):
    for point in coords:
        publish_location(point)
        # print("Published current location:", point)
        sleep(0.3)
        if stop_loop:
            return point
    return point
    

def publish_location(point):
    f = open('in_cam.json')
    m = json.load(f)
    m["latitude"] = point[1]
    m["longitude"] = point[0]
    m["stationID"] = boat_id
    m = json.dumps(m)
    client.publish("vanetza/in/cam",m)


# coordinates init
zone = eval(getenv('ZONE'))
min_tuple = min(zone, key=lambda tup: tup[1]+tup[0])
max_tuple = max(zone, key=lambda tup: tup[1]+tup[0])
cntrs = genCenters(min_tuple[1], min_tuple[0], max_tuple[1], max_tuple[0], int(getenv('MAP_PRCSN')))
sqnc_no = 0
closest = ()
stop_loop = False
#publica no in e recebe no out

# env init
boat_id = int(getenv('BOAT_ID'))
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.message_callback_add("vanetza/out/denm", foreign_discovery)
client.connect(getenv('BROKER_IP'), 1883, 60)

sleep(8)

# coms init 
curr_point = eval(getenv('START_POINT'))
publish_location(curr_point)
#publish_discovery(curr_point)

# computing init
print("Starting loop...")
mqtt_thread = threading.Thread(target=client.loop_forever)
mqtt_thread.start()

# looped task
while(True):
    if not cntrs:
        print("NOT CNTRS must stop")
        break
    stop_loop = False
    closest = calculate_closest(curr_point, cntrs)
    closest_distance = geodesic(curr_point,closest).m
    # print("Closest point is", closest, "with distance", closest_distance)
    move_ammount = int((closest_distance*int(getenv('MOV_AMNT')))/100)
    mov_coords = gen_coords(curr_point, closest, move_ammount)
    last_point=publish_movement(mov_coords)

    if closest==last_point:
        publish_discovery(last_point)
    curr_point = last_point

    # print("Cntrs left:", len(cntrs))
    if (len(cntrs)>48 and len(cntrs)<60):
        # make sure start point was sent
        publish_discovery(eval(getenv('START_POINT')))

# make sure start point was sent
publish_discovery(eval(getenv('START_POINT')))
client.loop_stop()
print("Reach end")
mqtt_thread.join()
