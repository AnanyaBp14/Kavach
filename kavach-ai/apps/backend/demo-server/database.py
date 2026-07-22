import sqlite3
import hashlib
import json
import random
import time
from pathlib import Path

DB_PATH = Path(__file__).parent / "kavach_demo.db"

def get_db_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Create Tables
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS complaints (
        id TEXT PRIMARY KEY,
        source TEXT,
        category TEXT,
        text_content TEXT,
        district TEXT,
        status TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS assessments (
        id TEXT PRIMARY KEY,
        complaint_id TEXT,
        overall_risk INTEGER,
        confidence REAL,
        agents_data TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS audit_logs (
        id TEXT PRIMARY KEY,
        evidence_hash TEXT,
        model_version TEXT,
        agent_versions TEXT,
        timestamp TEXT,
        action TEXT,
        status TEXT
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS reviews (
        id TEXT PRIMARY KEY,
        complaint_id TEXT,
        risk_score INTEGER,
        status TEXT,
        assigned_to TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS geo_incidents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        complaint_id TEXT,
        district TEXT,
        lat REAL,
        lon REAL,
        severity TEXT
    );
    """)

    conn.commit()

    # Seed Initial Users
    users = [
        ("citizen", hashlib.sha256("citizen123".encode()).hexdigest(), "Citizen"),
        ("police", hashlib.sha256("police123".encode()).hexdigest(), "Police Officer"),
        ("bank", hashlib.sha256("bank123".encode()).hexdigest(), "Bank Officer"),
        ("admin", hashlib.sha256("admin123".encode()).hexdigest(), "Admin")
    ]
    for u in users:
        cursor.execute("INSERT OR IGNORE INTO users (username, password_hash, role) VALUES (?, ?, ?)", u)

    # Seed 300 Complaints & Geo Incidents if empty
    cursor.execute("SELECT COUNT(*) FROM complaints")
    count = cursor.fetchone()[0]
    if count == 0:
        districts = [
            {"name": "Jamtara, JH", "lat": 23.9667, "lon": 86.8000},
            {"name": "Mewat, HR", "lat": 28.0000, "lon": 77.0000},
            {"name": "Bharatpur, RJ", "lat": 27.2167, "lon": 77.4833},
            {"name": "Bengaluru Urban, KA", "lat": 12.9716, "lon": 77.5946},
            {"name": "Cyberabad, TS", "lat": 17.4435, "lon": 78.3772}
        ]
        categories = ["UPI_FRAUD", "DIGITAL_ARREST", "PHISHING", "INVESTMENT_SCAM", "COUNTERFEIT_NOTE"]
        
        # Fraud Ring Alpha (Jamtara UPI Fraud - 25 complaints)
        for i in range(25):
            comp_id = f"COMP-A{i+1:03d}"
            dist = districts[0] # Jamtara
            cursor.execute(
                "INSERT INTO complaints (id, source, category, text_content, district, status) VALUES (?, ?, ?, ?, ?, ?)",
                (comp_id, "CITIZEN_PORTAL", "UPI_FRAUD", f"Victim paid money to UPI ID scammer@ybl via phone +91 98765 43210", dist["name"], "ACTIVE")
            )
            cursor.execute(
                "INSERT INTO geo_incidents (complaint_id, district, lat, lon, severity) VALUES (?, ?, ?, ?, ?)",
                (comp_id, dist["name"], dist["lat"] + random.uniform(-0.05, 0.05), dist["lon"] + random.uniform(-0.05, 0.05), "CRITICAL")
            )

        # Remaining ~275 complaints
        for i in range(26, 301):
            comp_id = f"COMP-{i:04d}"
            dist = random.choice(districts)
            cat = random.choice(categories)
            cursor.execute(
                "INSERT INTO complaints (id, source, category, text_content, district, status) VALUES (?, ?, ?, ?, ?, ?)",
                (comp_id, "CYBER_PORTAL", cat, f"Cyber fraud incident reported in {dist['name']}", dist["name"], "ACTIVE")
            )
            cursor.execute(
                "INSERT INTO geo_incidents (complaint_id, district, lat, lon, severity) VALUES (?, ?, ?, ?, ?)",
                (comp_id, dist["name"], dist["lat"] + random.uniform(-0.1, 0.1), dist["lon"] + random.uniform(-0.1, 0.1), random.choice(["HIGH", "MEDIUM", "LOW"]))
            )

        # Seed initial Audit Log
        evidence_hash = hashlib.sha256("sample_evidence_data".encode()).hexdigest()
        cursor.execute(
            "INSERT INTO audit_logs (id, evidence_hash, model_version, agent_versions, timestamp, action, status) VALUES (?, ?, ?, ?, ?, ?, ?)",
            ("AUD-1001", evidence_hash, "Llama-3.3-70b-versatile", "Scam:1.2, Vision:2.0, Graph:1.5, Geo:1.1", time.strftime("%Y-%m-%d %H:%M:%S"), "FUSION_ANALYSIS", "VERIFIED")
        )

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully!")
