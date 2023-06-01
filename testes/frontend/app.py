from flask import Flask, render_template, request, jsonify
from flask_mqtt import Mqtt
from os import getenv
import sys
import json

app = Flask(__name__)
app.template_folder = 'templates'
app.static_folder = 'static'
app.config['MQTT_BROKER_URL'] = getenv('BROKER_URL')
print("\n\n\n" + getenv('BROKER_URL') + "\n\n\n")
app.config['MQTT_BROKER_PORT'] = 1883
app.config['MQTT_CLIENT_ID'] = 'flask_api'
app.config['MQTT_KEEPALIVE'] = 5  # Set KeepAlive time in seconds
mqtt = Mqtt(app)

data = {'boats': [
        {'latitude': 0, 'longitude': 0, 'ID': 1},
        {'latitude': 0, 'longitude': 0, 'ID': 2},
        {'latitude': 0, 'longitude': 0, 'ID': 3}
        ]}

@mqtt.on_connect()
def handle_connect(client, userdata, flags, rc):
   if rc == 0:
       print('Connected successfully')
       mqtt.subscribe("vanetza/out/cam") 
   else:
       print('Bad connection. Code:', rc)

@mqtt.on_message()
def handle_mqtt_message(client, userdata, message):

    if message.topic=="vanetza/out/cam":
        payload = json.loads(message.payload.decode())
        bid = payload["stationID"]
        lat = payload["latitude"]
        lon = payload["longitude"]

        data['boats'][bid-1]['latitude']=lat
        data['boats'][bid-1]['longitude']=lon

        # print(bid, lat, lon, message.topic)
        # print(data)
        ##print('Received message on topic: {topic} with payload: {payload}'.format(**data))
        #sys.stdout.flush()
    else:
        print("Unrecongnized topic: " + message.topic)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api', methods=['POST'])
def receive_data():
    data = request.get_json()
    # process the GPS data as JSON  
    print(type(data))
    # iterate as dict
    # get the value of the key 'lat'
    Lat = data['Latitude']
    Lon = data['Longitude']
    Time_H = data['Time_H']
    Time_M = data['Time_M']
    Time_S = data['Time_S']
    Status = data['Status']
    Speed = data['Speed']
    Course = data['Course']


    # create time string using string formatting
    time = '{:02d}:{:02d}:{:02d}'.format(Time_H, Time_M, Time_S)

    GPS_info = [Lat, Lon, time, Status, Speed, Course]
    print(GPS_info)

    return 'Data received'


@app.route('/get_data', methods=['GET'])
def send_data():
    # Send boats coordinates to frontend
    return json.dumps(data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
