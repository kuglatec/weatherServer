import flask
import sqlite3
from datetime import datetime

app = flask.Flask(__name__)
DB_PATH = 'sensor_data.db'

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS sensors
                 (id INTEGER PRIMARY KEY, device_id TEXT, temperature REAL, humidity REAL, timestamp TEXT)''')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def index():
    return flask.render_template('index.html')

@app.route('/data', methods=['POST'])
def receive_sensor_data():
    data = flask.request.get_json()
    device_id = data.get('device_id')
    temperature = data.get('temperature')
    humidity = data.get('humidity')
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('INSERT INTO sensors (device_id, temperature, humidity, timestamp) VALUES (?, ?, ?, ?)',
              (device_id, temperature, humidity, datetime.now().isoformat()))
    conn.commit()
    conn.close()
    
    print(f"Saved: {data}")
    return flask.jsonify({'status': 'ok'}), 201
