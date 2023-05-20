from flask import Flask, render_template, jsonify, request
from obu_db_init import create_obu_db
import sqlite3


app = Flask(__name__)

@app.route('/')
def index():
    if request.is_json:
        
        conn = sqlite3.connect('obu.db')
        cursor = conn.cursor()
        obus = {} 

        cursor.execute("SELECT ip, lat, long FROM obu")
        rows = cursor.fetchall()
        
        for row in rows:
            obus.update({row[0]: {"latitude": row[1], "longitude": row[2]}})
        
        conn.close()
        
        return jsonify(obus)
    
    return render_template('map.html')

if __name__ == '__main__':
    create_obu_db()
    app.run(debug = True)