from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os, json

app = Flask(__name__, static_folder='static')
CORS(app)

# ── Database: PostgreSQL se disponibile, SQLite come fallback locale ──────────
DATABASE_URL = os.environ.get('DATABASE_URL', '')

if DATABASE_URL:
    import psycopg2
    from psycopg2.extras import RealDictCursor

    def get_db():
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        return conn

    def init_db():
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute('''CREATE TABLE IF NOT EXISTS storage (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    updated_at TIMESTAMP DEFAULT NOW()
                )''')
            conn.commit()

    def db_get(key):
        with get_db() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute('SELECT value FROM storage WHERE key = %s', (key,))
                row = cur.fetchone()
                return row['value'] if row else None

    def db_set(key, value):
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute('''INSERT INTO storage (key, value) VALUES (%s, %s)
                    ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value, updated_at = NOW()''',
                    (key, value))
            conn.commit()

    def db_delete(key):
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute('DELETE FROM storage WHERE key = %s', (key,))
            conn.commit()

    def db_list(prefix):
        with get_db() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute('SELECT key FROM storage WHERE key LIKE %s', (prefix + '%',))
                return [r['key'] for r in cur.fetchall()]

else:
    import sqlite3

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

    def db_get(key):
        db = get_db()
        row = db.execute('SELECT value FROM storage WHERE key = ?', (key,)).fetchone()
        return row['value'] if row else None

    def db_set(key, value):
        with get_db() as db:
            db.execute('''INSERT INTO storage (key, value) VALUES (?, ?)
                ON CONFLICT(key) DO UPDATE SET value=excluded.value, updated_at=CURRENT_TIMESTAMP''',
                (key, value))
            db.commit()

    def db_delete(key):
        with get_db() as db:
            db.execute('DELETE FROM storage WHERE key = ?', (key,))
            db.commit()

    def db_list(prefix):
        db = get_db()
        rows = db.execute('SELECT key FROM storage WHERE key LIKE ?', (prefix + '%',)).fetchall()
        return [r['key'] for r in rows]

init_db()

# ── Routes ────────────────────────────────────────────────────────────────────
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
