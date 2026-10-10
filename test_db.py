"""Test database functionality."""

import db
import os
import sqlite3


def test_database():
    """Test database creation and logging."""
    print("Testing database functionality...")
    
    # Test 1: Check if database file is created
    if os.path.exists("academic_twin.db"):
        print("✓ Database file exists")
    else:
        print("✗ Database file not found")
        return
    
    # Test 2: Test log_interaction function
    print("\nTest 2: Logging interactions")
    try:
        interaction_id1 = db.log_interaction(
            student_id="test_student_1",
            topic="Kinematics",
            engagement_seconds=120.5,
            score_delta=2.5
        )
        print(f"✓ Logged interaction 1 with ID: {interaction_id1}")
        
        interaction_id2 = db.log_interaction(
            student_id="test_student_2",
            topic="Thermodynamics",
            engagement_seconds=180.0,
            score_delta=-1.0
        )
        print(f"✓ Logged interaction 2 with ID: {interaction_id2}")
        
    except Exception as e:
        print(f"✗ Failed to log interactions: {e}")
        return
    
    # Test 3: Test get_student_history
    print("\nTest 3: Retrieving student history")
    try:
        history = db.get_student_history("test_student_1")
        print(f"✓ Retrieved {len(history)} interactions for test_student_1")
        if history:
            print(f"  Latest: {history[0]['datetime']} - Topic: {history[0]['topic']}")
    except Exception as e:
        print(f"✗ Failed to get student history: {e}")
    
    # Test 4: Test get_db_stats
    print("\nTest 4: Database statistics")
    try:
        stats = db.get_db_stats()
        print(f"✓ Total interactions: {stats['total_interactions']}")
        print(f"✓ Unique students: {stats['unique_students']}")
        print(f"✓ Total engagement hours: {stats['total_engagement_hours']:.2f}")
        print(f"✓ Topic counts: {stats['topic_counts']}")
    except Exception as e:
        print(f"✗ Failed to get stats: {e}")
    
    # Test 5: Test invalid topic validation
    print("\nTest 5: Invalid topic validation")
    try:
        db.log_interaction(
            student_id="test_student_3",
            topic="InvalidTopic",
            engagement_seconds=100.0,
            score_delta=1.0
        )
        print("✗ Should have raised ValueError for invalid topic")
    except ValueError as e:
        print(f"✓ Correctly raised ValueError: {e}")
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
    
    # Test 6: Direct SQLite verification
    print("\nTest 6: Direct database verification")
    try:
        conn = sqlite3.connect("academic_twin.db")
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print(f"✓ Tables in database: {[t[0] for t in tables]}")
        
        cursor.execute("SELECT * FROM interactions LIMIT 5")
        rows = cursor.fetchall()
        print(f"✓ Found {len(rows)} rows in interactions table")
        conn.close()
    except Exception as e:
        print(f"✗ Database verification failed: {e}")
    
    print("\n" + "="*50)
    print("Database test complete")


if __name__ == "__main__":
    test_database()