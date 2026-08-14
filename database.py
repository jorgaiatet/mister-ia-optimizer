"""
Database & persistence layer for Mister IA Optimizer Pro.
Stores user settings, active tokens, and historical team tracking.
"""

import sqlite3
import os
import json

DB_PATH = "mister_optimizer.db"

JWT_PERMANENT_TOKEN = "eyJhbGciOiJFUzI1NiJ9.eyJleHAiOiIxNzg2NzIyODUzIiwidXNlcmlkIjoiMjk0Nzk4MiIsImFsZyI6IkVTMjU2In0.IA04fQXwxyXRc_QhVJU0MCmMwQ5hHCFRmOzd5-MZS3YaV8NhO0hGl4ZU7yeBfdmXAaRVEMxiX7Ps3seZ1k0FPA"
PHPSESSID_COOKIE = "f3b48c91205f19bf35bcf23bc566e941"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS historical_squads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            squad_json TEXT,
            saldo REAL,
            team_val REAL
        )
    ''')
    conn.commit()
    conn.close()

def get_setting(key: str, default: str = "") -> str:
    init_db()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT value FROM settings WHERE key = ?', (key,))
    row = c.fetchone()
    conn.close()
    if row:
        return row[0]
    if key in ["mister_token", "jwt_token"]:
        return JWT_PERMANENT_TOKEN
    if key == "phpsessid":
        return PHPSESSID_COOKIE
    return default

def set_setting(key: str, value: str):
    init_db()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)', (key, str(value)))
    conn.commit()
    conn.close()

def save_squad_snapshot(squad: list, saldo: float, team_val: float):
    init_db()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('INSERT INTO historical_squads (squad_json, saldo, team_val) VALUES (?, ?, ?)',
              (json.dumps(squad, ensure_ascii=False), saldo, team_val))
    conn.commit()
    conn.close()

# Initialize on module load
init_db()
set_setting("mister_token", JWT_PERMANENT_TOKEN)
set_setting("jwt_token", JWT_PERMANENT_TOKEN)
set_setting("phpsessid", PHPSESSID_COOKIE)
