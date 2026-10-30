import sqlite3
import os
from config import Config

def get_db_connection():
    """Returns a SQLite connection with row factory enabled."""
    os.makedirs(os.path.dirname(Config.DATABASE_PATH), exist_ok=True)
    conn = sqlite3.connect(Config.DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    """Initializes the database schema if tables do not exist and applies migrations."""
    schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
    with open(schema_path, 'r') as f:
        schema_sql = f.read()
    
    conn = get_db_connection()
    try:
        # Check if complaints table exists without latitude/longitude
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='complaints'")
        if cursor.fetchone():
            cursor.execute("PRAGMA table_info(complaints)")
            cols = [row[1] for row in cursor.fetchall()]
            if 'latitude' not in cols:
                cursor.execute("ALTER TABLE complaints ADD COLUMN latitude REAL")
            if 'longitude' not in cols:
                cursor.execute("ALTER TABLE complaints ADD COLUMN longitude REAL")
            if 'is_synthetic' not in cols:
                cursor.execute("ALTER TABLE complaints ADD COLUMN is_synthetic INTEGER DEFAULT 0")
                cursor.execute("UPDATE complaints SET is_synthetic = 1 WHERE tracking_id LIKE '%SYN%' OR citizen_name LIKE '%Synthetic%'")
            conn.commit()

        conn.executescript(schema_sql)
        conn.commit()
    finally:
        conn.close()

def query_db(query, args=(), one=False):
    """Utility to query database and return dictionary rows."""
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute(query, args)
        rv = cur.fetchall()
        cur.close()
        return (dict(rv[0]) if rv else None) if one else [dict(r) for r in rv]
    finally:
        conn.close()

def execute_db(query, args=()):
    """Utility to execute insert/update/delete and return lastrowid or affected rows."""
    conn = get_db_connection()
    try:
        with conn:
            cur = conn.cursor()
            cur.execute(query, args)
            last_id = cur.lastrowid
            cur.close()
            return last_id
    finally:
        conn.close()

def log_activity(complaint_id, action, details="", actor="System"):
    """Adds an entry to the activity log."""
    query = """
        INSERT INTO activity_logs (complaint_id, action, details, actor)
        VALUES (?, ?, ?, ?)
    """
    execute_db(query, (complaint_id, action, details, actor))

