import sqlite3
import json
import os
from typing import List, Dict, Any, Optional

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "applications.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            company_name TEXT NOT NULL,
            role_title TEXT NOT NULL,
            location TEXT,
            match_score INTEGER DEFAULT 0,
            status TEXT DEFAULT 'Draft',
            career_level TEXT DEFAULT 'student',
            data_json TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def save_application(
    company_name: str,
    role_title: str,
    location: str,
    match_score: int,
    data: dict,
    status: str = "Draft",
    career_level: str = "student"
) -> int:
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO applications (company_name, role_title, location, match_score, status, career_level, data_json)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        company_name or "Company",
        role_title or "Role",
        location or "",
        match_score or 0,
        status,
        career_level,
        json.dumps(data)
    ))
    new_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return new_id

def get_all_applications() -> List[Dict[str, Any]]:
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, created_at, company_name, role_title, location, match_score, status, career_level
        FROM applications
        ORDER BY id DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    
    results = []
    for r in rows:
        results.append({
            "id": r[0],
            "created_at": r[1],
            "company_name": r[2],
            "role_title": r[3],
            "location": r[4],
            "match_score": r[5],
            "status": r[6],
            "career_level": r[7]
        })
    return results

def get_application(app_id: int) -> Optional[Dict[str, Any]]:
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, created_at, company_name, role_title, location, match_score, status, career_level, data_json
        FROM applications
        WHERE id = ?
    """, (app_id,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return None
    
    return {
        "id": row[0],
        "created_at": row[1],
        "company_name": row[2],
        "role_title": row[3],
        "location": row[4],
        "match_score": row[5],
        "status": row[6],
        "career_level": row[7],
        "data": json.loads(row[8])
    }

def update_application_status(app_id: int, new_status: str):
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE applications SET status = ? WHERE id = ?", (new_status, app_id))
    conn.commit()
    conn.close()

def delete_application(app_id: int):
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM applications WHERE id = ?", (app_id,))
    conn.commit()
    conn.close()

