from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os, json, sqlite3

app = Flask(__name__, static_folder='static')
CORS(app)

DATABASE_URL = os.environ.get('DATABASE_URL', '')

# Render fornisce URL con prefisso "postgres://" ma psycopg2 vuole "postgresql://"
if DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

USE_PG = bool(DATABASE_URL)

if USE_PG:
    import psycopg2
    from psycopg2.extras import RealDictCursor

    def get_conn():
        return psycopg2.connect(DATABASE_URL)

    def init_db():
        conn = get_conn()
        cur = conn.cursor()
        cur.execute('''CREATE TABLE IF NOT EXISTS storage (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL,
            updated_at TIMESTAMP DEFAULT NOW()
        )''')
        conn.commit()
        cur.close()
        conn.close()

    def db_get(key):
        conn = get_conn()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute('SELECT value FROM storage WHERE key = %s', (key,))
        row = cur.fetchone()
        cur.close(); conn.close()
        return row['value'] if row else None

    def db_set(key, value):
        conn = get_conn()
        cur = conn.cursor()
        cur.execute('''INSERT INTO storage (key, value) VALUES (%s, %s)
            ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value, updated_at = NOW()''',
            (key, value))
        conn.commit()
        cur.close(); conn.close()

    def db_delete(key):
        conn = get_conn()
        cur = conn.cursor()
        cur.execute('DELETE FROM storage WHERE key = %s', (key,))
        conn.commit()
        cur.close(); conn.close()

    def db_list(prefix):
        conn = get_conn()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute('SELECT key FROM storage WHERE key LIKE %s', (prefix + '%',))
        rows = cur.fetchall()
        cur.close(); conn.close()
        return [r['key'] for r in rows]

else:
    def get_conn():
        conn = sqlite3.connect('spese.db')
        conn.row_factory = sqlite3.Row
        return conn

    def init_db():
        conn = get_conn()
        conn.execute('''CREATE TABLE IF NOT EXISTS storage (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )''')
        conn.commit()
        conn.close()

    def db_get(key):
        conn = get_conn()
        row = conn.execute('SELECT value FROM storage WHERE key = ?', (key,)).fetchone()
        conn.close()
        return row['value'] if row else None

    def db_set(key, value):
        conn = get_conn()
        conn.execute('''INSERT INTO storage (key, value) VALUES (?, ?)
            ON CONFLICT(key) DO UPDATE SET value=excluded.value''', (key, value))
        conn.commit()
        conn.close()

    def db_delete(key):
        conn = get_conn()
        conn.execute('DELETE FROM storage WHERE key = ?', (key,))
        conn.commit()
        conn.close()

    def db_list(prefix):
        conn = get_conn()
        rows = conn.execute('SELECT key FROM storage WHERE key LIKE ?', (prefix + '%',)).fetchall()
        conn.close()
        return [r['key'] for r in rows]

init_db()

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/api/storage/<key>', methods=['GET'])
def storage_get(key):
    value = db_get(key)
    if value is not None:
        return jsonify({'key': key, 'value': value})
    return jsonify(None), 404

@app.route('/api/storage/<key>', methods=['POST'])
def storage_set(key):
    data = request.get_json()
    value = data.get('value', '')
    db_set(key, value)
    return jsonify({'key': key, 'value': value})

@app.route('/api/storage/<key>', methods=['DELETE'])
def storage_delete(key):
    db_delete(key)
    return jsonify({'key': key, 'deleted': True})

@app.route('/api/storage', methods=['GET'])
def storage_list():
    prefix = request.args.get('prefix', '')
    return jsonify({'keys': db_list(prefix)})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
