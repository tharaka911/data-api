from flask import Flask, request, jsonify
import sqlite3
import os
from datetime import datetime
import pytz

app = Flask(__name__)
DATABASE = 'data.db'
TIMEZONE = pytz.timezone('Asia/Kolkata')  # UTC+5:30

def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    # Create data table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            temperature REAL NOT NULL,
            humidity REAL NOT NULL,
            timestamp TEXT NOT NULL
        )
    ''')
    # Create status table if it doesn't exist, with a single row to store the status value
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS status (
            id INTEGER PRIMARY KEY,
            value BOOLEAN NOT NULL
        )
    ''')
    # Initialize the status to False if not already set
    cursor.execute('INSERT OR IGNORE INTO status (id, value) VALUES (1, 0)')
    conn.commit()
    conn.close()

@app.route('/save', methods=['POST'])
def save_data():
    data = request.get_json()
    temperature = data.get('temperature')
    humidity = data.get('humidity')

    if temperature is None or humidity is None:
        return 'Temperature and humidity are required', 400

    timestamp = datetime.now(TIMEZONE).isoformat()
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO data (temperature, humidity, timestamp)
        VALUES (?, ?, ?)
    ''', (temperature, humidity, timestamp))
    conn.commit()
    conn.close()

    return 'Data saved successfully', 200

@app.route('/retrieve', methods=['GET'])
def retrieve_data():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('SELECT temperature, humidity, timestamp FROM data')
    rows = cursor.fetchall()
    conn.close()

    data = [{'temperature': row[0], 'humidity': row[1], 'timestamp': row[2]} for row in rows]
    return jsonify(data), 200

# Endpoint to update the status
@app.route('/status/update', methods=['POST'])
def update_status():
    data = request.get_json()
    status = data.get('status')

    if status is None:
        return 'Status is required', 400

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('UPDATE status SET value = ? WHERE id = 1', (1 if status else 0,))
    conn.commit()
    conn.close()

    return 'Status updated successfully', 200

# Endpoint to get the current status
@app.route('/status', methods=['GET'])
def get_status():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('SELECT value FROM status WHERE id = 1')
    status = cursor.fetchone()[0]
    conn.close()

    return jsonify({'status': bool(status)}), 200

if __name__ == '__main__':
    init_db()
    port = int(os.getenv("PORT", 3000))
    app.run(host='0.0.0.0', port=port)
