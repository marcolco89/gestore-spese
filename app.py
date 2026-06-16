from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import sqlite3, os, json

app = Flask(__name__, static_folder='static')
CORS(app)

DB = os.environ.get('DATABASE_URL', 'spese.db')

def get_db():
    conn = sqlite3.connect('spese.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as db:
        db.execute('''CREATE TABLE IF NOT EXISTS storage (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )''')
        db.commit()

init_db()

# Serve l'app HTML
@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

# API storage — compatibile con window.storage usato nell'HTML
@app.route('/api/storage/<key>', methods=['GET'])
def storage_get(key):
    db = get_db()
    row = db.execute('SELECT value FROM storage WHERE key = ?', (key,)).fetchone()
    if row:
        return jsonify({'key': key, 'value': row['value']})
    return jsonify(None), 404

@app.route('/api/storage/<key>', methods=['POST'])
def storage_set(key):
    data = request.get_json()
    value = data.get('value', '')
    with get_db() as db:
        db.execute('''INSERT INTO storage (key, value) VALUES (?, ?)
            ON CONFLICT(key) DO UPDATE SET value=excluded.value, updated_at=CURRENT_TIMESTAMP''',
            (key, value))
        db.commit()
    return jsonify({'key': key, 'value': value})

@app.route('/api/storage/<key>', methods=['DELETE'])
def storage_delete(key):
    with get_db() as db:
        db.execute('DELETE FROM storage WHERE key = ?', (key,))
        db.commit()
    return jsonify({'key': key, 'deleted': True})

@app.route('/api/storage', methods=['GET'])
def storage_list():
    prefix = request.args.get('prefix', '')
    db = get_db()
    rows = db.execute('SELECT key FROM storage WHERE key LIKE ?', (prefix + '%',)).fetchall()
    return jsonify({'keys': [r['key'] for r in rows]})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
