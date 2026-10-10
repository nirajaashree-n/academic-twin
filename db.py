"""SQLite database for Academic Twin interactions."""

import sqlite3
import time
from typing import List, Dict, Any, Optional
from datetime import datetime


# Hardcoded topics list
TOPICS = ["Kinematics", "Thermodynamics", "Calculus", "Physics", "Chemistry", "Biology"]


def init_db():
    """Initialize the SQLite database."""
    conn = sqlite3.connect("academic_twin.db")
    cursor = conn.cursor()
    
    # Create interactions table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS interactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            topic TEXT NOT NULL,
            timestamp REAL NOT NULL,
            engagement_seconds REAL NOT NULL,
            score_delta REAL NOT NULL
        )
    """)
    
    # Create index for faster student queries
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_student_id ON interactions (student_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON interactions (timestamp)")
    
    conn.commit()
    conn.close()


def log_interaction(student_id: str, topic: str, engagement_seconds: float, score_delta: float) -> int:
    """
    Log an interaction to the database.
    
    Args:
        student_id: Student identifier
        topic: Learning topic (must be in TOPICS list)
        engagement_seconds: Total engagement seconds for this interaction
        score_delta: Score change for this interaction
        
    Returns:
        Interaction ID
    """
    # Validate topic
    # Accept any topic string from Gemini
    
    timestamp = time.time()
    
    conn = sqlite3.connect("academic_twin.db")
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO interactions (student_id, topic, timestamp, engagement_seconds, score_delta)
        VALUES (?, ?, ?, ?, ?)
    """, (student_id, topic, timestamp, engagement_seconds, score_delta))
    
    interaction_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return interaction_id


def get_student_history(student_id: str, limit: int = 100) -> List[Dict[str, Any]]:
    """
    Get interaction history for a student.
    
    Args:
        student_id: Student identifier
        limit: Maximum number of records to return
        
    Returns:
        List of interaction dictionaries
    """
    conn = sqlite3.connect("academic_twin.db")
    conn.row_factory = sqlite3.Row  # Return rows as dictionaries
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, student_id, topic, timestamp, engagement_seconds, score_delta
        FROM interactions
        WHERE student_id = ?
        ORDER BY timestamp DESC
        LIMIT ?
    """, (student_id, limit))
    
    rows = cursor.fetchall()
    conn.close()
    
    # Convert to list of dictionaries
    result = []
    for row in rows:
        result.append({
            "id": row["id"],
            "student_id": row["student_id"],
            "topic": row["topic"],
            "timestamp": row["timestamp"],
            "engagement_seconds": row["engagement_seconds"],
            "score_delta": row["score_delta"],
            "datetime": datetime.fromtimestamp(row["timestamp"]).strftime("%Y-%m-%d %H:%M:%S")
        })
    
    return result


def get_db_stats() -> Dict[str, Any]:
    """Get database statistics."""
    conn = sqlite3.connect("academic_twin.db")
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM interactions")
    total_interactions = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(DISTINCT student_id) FROM interactions")
    unique_students = cursor.fetchone()[0]
    
    cursor.execute("SELECT SUM(engagement_seconds) FROM interactions")
    total_engagement = cursor.fetchone()[0] or 0
    
    cursor.execute("SELECT topic, COUNT(*) FROM interactions GROUP BY topic ORDER BY COUNT(*) DESC")
    topic_counts = cursor.fetchall()
    
    conn.close()
    
    return {
        "total_interactions": total_interactions,
        "unique_students": unique_students,
        "total_engagement_hours": total_engagement / 3600,
        "topic_counts": dict(topic_counts)
    }


# Initialize database when module is imported
init_db()
