import sqlite3
import os
import json
from datetime import datetime
from pathlib import Path

# Create db directory if it doesn't exist
DB_DIR = Path(__file__).parent
DB_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = DB_DIR / "shiksha.db"

def get_db_connection():
    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Request Logs Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS request_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            endpoint TEXT,
            language TEXT,
            response_time_ms REAL,
            question_length INTEGER,
            status_code INTEGER,
            session_id TEXT
        )
    ''')
    
    # Chat History Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            role TEXT NOT NULL,
            content TEXT NOT NULL
        )
    ''')
    
    conn.commit()
    conn.close()

def log_request(endpoint: str, language: str, response_time_ms: float, question_length: int, status_code: int, session_id: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        '''INSERT INTO request_logs 
           (endpoint, language, response_time_ms, question_length, status_code, session_id)
           VALUES (?, ?, ?, ?, ?, ?)''',
        (endpoint, language, response_time_ms, question_length, status_code, session_id)
    )
    conn.commit()
    conn.close()

def save_chat_message(session_id: str, role: str, content: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO chat_history (session_id, role, content) VALUES (?, ?, ?)',
        (session_id, role, content)
    )
    conn.commit()
    conn.close()

def get_chat_history(session_id: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'SELECT role, content, timestamp FROM chat_history WHERE session_id = ? ORDER BY timestamp ASC',
        (session_id,)
    )
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]
