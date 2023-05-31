from flask import Flask, render_template, request, jsonify
from flask_mqtt import Mqtt
from os import getenv
#import sys
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

Lat, Lon, time = 37.87400, -25.78800, "08:46:36"
Status, Speed, Course = 0, 0, 0

@mqtt.on_connect()
def handle_connect(client, userdata, flags, rc):
   if rc == 0:
       print('Connected successfully')
       mqtt.subscribe("vanetza/out/denm") 
   else:
       print('Bad connection. Code:', rc)

@mqtt.on_message()
def handle_mqtt_message(client, userdata, message):
   data = dict(
       topic=message.topic,
       payload=message.payload.decode()
  )
   print('Received message on topic: {topic} with payload: {payload}'.format(**data))
   #sys.stdout.flush()

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
    global Lon
    Lon += 0.00001
    data = {
            'boats': [
                {'Latitude': Lat, 'Longitude': Lon, 'ID': 1},
                {'Latitude': Lat, 'Longitude': Lon, 'ID': 2},
                {'Latitude': Lat, 'Longitude': Lon, 'ID': 3}
                ]
            }

    return json.dumps(data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
