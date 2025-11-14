# db.py

import sqlite3, os


DB_PATH = os.path.join(os.path.dirname(__file__), "dementia_care.db") # looks for this python file's folder and concats

def get_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foriegn_keys = ON;")
    return conn

def query_db(query, args=(), one=False):
    conn = gen_connection()
    cur = conn.execute(query, args)
    rows = cur.fetchall()
    conn.close()
    return (rows[0] if rows else None) if one else rows

def execute_db(query, args=()):
    conn = get_connection()
    conn.execute(query, args)
    conn.commit()
    conn.close()