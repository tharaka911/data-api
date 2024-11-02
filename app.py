from flask import Flask, request, jsonify
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)
DATABASE = 'data.db'

def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            temperature REAL NOT NULL,
            humidity REAL NOT NULL,
            timestamp TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/save', methods=['POST'])
def save_data():
    data = request.get_json()
    temperature = data.get('temperature')
    humidity = data.get('humidity')

    if temperature is None or humidity is None:
        return 'Temperature and humidity are required', 400

    timestamp = datetime.now().isoformat()
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


if __name__ == '__main__':
    init_db()
    port = int(os.getenv("PORT", 3000))
    app.run(host='0.0.0.0', port=port)
