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
    c.execute('''CREATE TABLE IF NOT EXISTS device_aliases
                 (device_id TEXT PRIMARY KEY, alias TEXT)''')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def index():
    return flask.render_template('index.html')

@app.route('/api/data')
def get_sensor_data():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT device_id, temperature, humidity, timestamp FROM sensors ORDER BY timestamp DESC LIMIT 100')
    rows = c.fetchall()

    # Get all aliases
    c.execute('SELECT device_id, alias FROM device_aliases')
    aliases = dict(c.fetchall())
    conn.close()

    data = []
    for row in rows:
        device_id = row[0]
        data.append({
            'device_id': device_id,
            'alias': aliases.get(device_id, ''),
            'temperature': row[1],
            'humidity': row[2],
            'timestamp': row[3]
        })

    return flask.jsonify(data)

@app.route('/api/submit', methods=['POST'])
def submit_sensor_data():
    data = flask.request.get_json()

    if not data or 'device_id' not in data or 'temperature' not in data or 'humidity' not in data:
        return flask.jsonify({'error': 'Missing required fields'}), 400

    device_id = data['device_id']
    temperature = data['temperature']
    humidity = data['humidity']
    timestamp = datetime.now().isoformat()

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('INSERT INTO sensors (device_id, temperature, humidity, timestamp) VALUES (?, ?, ?, ?)',
              (device_id, temperature, humidity, timestamp))
    conn.commit()
    conn.close()

    return flask.jsonify({'status': 'success', 'timestamp': timestamp}), 201

@app.route('/api/set-alias', methods=['POST'])
def set_alias():
    data = flask.request.get_json()

    if not data or 'device_id' not in data or 'alias' not in data:
        return flask.jsonify({'error': 'Missing required fields'}), 400

    device_id = data['device_id']
    alias = data['alias']

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('INSERT OR REPLACE INTO device_aliases (device_id, alias) VALUES (?, ?)',
              (device_id, alias))
    conn.commit()
    conn.close()

    return flask.jsonify({'status': 'success'}), 200

@app.route('/api/delete-device/<device_id>', methods=['DELETE'])
def delete_device(device_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('DELETE FROM sensors WHERE device_id = ?', (device_id,))
    c.execute('DELETE FROM device_aliases WHERE device_id = ?', (device_id,))
    conn.commit()
    conn.close()

    return flask.jsonify({'status': 'success'}), 200

@app.route('/api/clear-readings/<device_id>', methods=['DELETE'])
def clear_readings(device_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('DELETE FROM sensors WHERE device_id = ?', (device_id,))
    conn.commit()
    conn.close()

    return flask.jsonify({'status': 'success'}), 200
