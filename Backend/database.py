import sqlite3
import logging
from datetime import datetime
from backend.config import DATA_DIR

logger = logging.getLogger("PosturaX.Database")
DB_PATH = DATA_DIR / "posturax.db"

def init_db():
    """Database tables setup karta hai."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS posture_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                pitch REAL,
                deviation REAL,
                status TEXT
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS slouch_episodes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                start_time DATETIME,
                end_time DATETIME,
                duration_seconds REAL,
                max_intervention TEXT
            )
        """)
        conn.commit()
    logger.info("Database initialized successfully.")

def log_telemetry(pitch: float, deviation: float, status: str):
    """Har incoming reading ko database me save karta hai."""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO posture_logs (pitch, deviation, status) VALUES (?, ?, ?)",
                (pitch, deviation, status)
            )
            conn.commit()
    except Exception as e:
        logger.error(f"Failed to log telemetry: {e}")

def get_today_summary() -> dict:
    """Dashboard ke liye aaj ke din ke statistics fetch karta hai."""
    today_str = datetime.now().strftime("%Y-%m-%d")
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                COUNT(*) as total_readings,
                SUM(CASE WHEN status = 'FORWARD_SLOUCHING' THEN 1 ELSE 0 END) as slouch_readings,
                AVG(deviation) as avg_deviation
            FROM posture_logs 
            WHERE DATE(timestamp) = ?
        """, (today_str,))
        row = cursor.fetchone()
        
        total = row[0] or 0
        slouch = row[1] or 0
        avg_dev = round(row[2] or 0.0, 2)
        score = max(0, round(100 - (slouch / total * 100))) if total > 0 else 100

        return {
            "total_readings": total,
            "slouch_count": slouch,
            "avg_deviation": avg_dev,
            "posture_score": score
        }
