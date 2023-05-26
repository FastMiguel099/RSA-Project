from geographiclib.geodesic import Geodesic
import sqlite3, json, time
from datetime import datetime

def update_db(latitude, longitude, obu_id):
    obu_ips = {
        'obu1': "192.168.98.20",
        'obu2': "192.168.98.30",
        'obu3': "192.168.98.40"
    }

    try:
        obu_ip = obu_ips[obu_id]
    except KeyError:
        raise ValueError(f"Invalid OBU ID: {obu_id}")
    
    try:
        with sqlite3.connect('../obu.db') as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE obu SET lat = ?, long = ? WHERE ip = ?",
                (latitude, longitude, obu_ip)
            )
            conn.commit()
            
    except sqlite3.Error as e:
        print(f"Database error occurred: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

'''
def navigate_to_zone(start_point, zone_vertices, data, obu):
    closest_vertex = find_closest_point(start_point, zone_vertices)
    return navigate_to_point(start_point, closest_vertex, data, obu)
'''

def navigate_to_point(start_point, destination_point, data, obu, max_step_distance=100):
    geod = Geodesic.WGS84
    current_position = start_point
    
    while True:    
        result = geod.Inverse(*current_position, *destination_point)
        distance, bearing = result['s12'], result['azi1']
        step_distance = min(max_step_distance, distance)

        result = geod.Direct(*current_position, bearing, step_distance)
        current_position = (result['lat2'], result['lon2'])
        update_db(result['lat2'], result['lon2'], obu._client_id.decode("utf-8"))
        time.sleep(0.1)
        '''
        data['longitute'] = result['lon2']
        data['latitude'] = result['lat2']
        data['timestamp'] = datetime.timestamp(datetime.now())
        obu.publish("vanetza/in/cam", json.dumps(data))
        '''
        if (distance - step_distance) == 0:
            break

    return current_position

'''
def closest_points(n, start_point, zone, points_to_discover):
    closests_points = set()
    vertex_closests_points = {}

    for vertex in zone:
        if vertex == start_point:
            continue

        available_points = [p for p in points_to_discover if p not in closests_points]
        closest_points = sorted(available_points, key=lambda p: calculate_distance(vertex, p))[:n]

        closests_points.update(closest_points)
        vertex_closests_points[vertex] = closest_points

    return vertex_closests_points
'''