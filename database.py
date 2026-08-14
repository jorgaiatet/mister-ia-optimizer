"""
SQLite Database module for Mister IA Optimizer Pro.
Persists settings, credentials, and analysis history.
"""

import sqlite3
import os
import json
import logging

logger = logging.getLogger("database")
DB_PATH = os.path.join(os.path.dirname(__file__), "mister_data.db")

def get_connection():
    try:
        conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn
    except Exception as e:
        logger.warning(f"Failed to connect to SQLite db on disk: {e}. Using in-memory database.")
        conn = sqlite3.connect(":memory:", check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

def init_db():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS analysis_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                squad_json TEXT,
                market_json TEXT,
                saldo REAL,
                report_json TEXT
            )
        """)
        conn.commit()
        conn.close()
    except Exception as e:
        logger.warning(f"Error initializing db tables: {e}")

def set_setting(key: str, value: str):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, str(value)))
        conn.commit()
        conn.close()
    except Exception as e:
        logger.warning(f"Error setting db setting {key}: {e}")

def get_setting(key: str, default: str = None) -> str:
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
        row = cursor.fetchone()
        conn.close()
        return row["value"] if row else default
    except Exception as e:
        logger.warning(f"Error getting db setting {key}: {e}")
        return default

# Initialize DB on load and set permanent active session cookie
init_db()
set_setting("mister_token", "f3b48c91205f19bf35bcf23bc566e941")
