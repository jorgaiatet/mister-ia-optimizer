"""
SQLite database module for Mister IA Optimizer Pro.
Handles saving user settings, credentials, historical reports, and market watchlists.
"""

import sqlite3
import json
import os
from typing import Optional, Dict, List, Any

DB_PATH = os.path.join(os.path.dirname(__file__), "mister_data.db")

def get_connection():
    """Get connection to SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize database tables if they do not exist."""
    with get_connection() as conn:
        cursor = conn.cursor()
        
        # User credentials & settings table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        # Saved historical reports table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS reports_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            squad_json TEXT,
            market_json TEXT,
            report_json TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        # Player Watchlist table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS watchlist (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            player_name TEXT NOT NULL UNIQUE,
            position TEXT,
            team TEXT,
            target_price REAL,
            notes TEXT,
            added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        conn.commit()

# Setting Helpers
def set_setting(key: str, value: str):
    """Save setting to database."""
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO settings (key, value, updated_at) VALUES (?, ?, CURRENT_TIMESTAMP) ON CONFLICT(key) DO UPDATE SET value=excluded.value, updated_at=CURRENT_TIMESTAMP",
            (key, value)
        )
        conn.commit()

def get_setting(key: str, default: str = "") -> str:
    """Retrieve setting from database."""
    with get_connection() as conn:
        row = conn.execute("SELECT value FROM settings WHERE key = ?", (key,)).fetchone()
        return row["value"] if row else default

# Report Helpers
def save_report_to_history(title: str, report_dict: dict, squad: list = None, market: list = None):
    """Save generated report to database history."""
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO reports_history (title, squad_json, market_json, report_json) VALUES (?, ?, ?, ?)",
            (
                title,
                json.dumps(squad or [], ensure_ascii=False),
                json.dumps(market or [], ensure_ascii=False),
                json.dumps(report_dict, ensure_ascii=False)
            )
        )
        conn.commit()

def get_reports_history(limit: int = 10) -> List[Dict[str, Any]]:
    """Retrieve historical reports."""
    with get_connection() as conn:
        rows = conn.execute("SELECT * FROM reports_history ORDER BY created_at DESC LIMIT ?", (limit,)).fetchall()
        result = []
        for r in rows:
            result.append({
                "id": r["id"],
                "title": r["title"],
                "created_at": r["created_at"],
                "report": json.loads(r["report_json"])
            })
        return result

# Initialize DB on module load
init_db()
