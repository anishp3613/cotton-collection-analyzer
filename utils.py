# utils.py

import sqlite3
import os

DATA_PATH = "data/data.db"

def init_db():
    if not os.path.exists("data"):
        os.mkdir("data")
    conn = sqlite3.connect(DATA_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            worker_name TEXT,
            cotton_kg REAL,
            rate_per_kg REAL,
            sale_rate_quintal REAL
        );
    """)
    conn.commit()
    conn.close()
