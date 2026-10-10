"""Integration test for Academic Twin with database."""

import sqlite3
import time
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db import log_interaction, get_student_history, get_db_stats, TOPICS
from api.services import interact_with_twin


def test_integration():
    """Test the integration between API, database, and app logic."""
    print("="*60)
    print("Academic Twin Integration Test")
    print("="*60)
    
    # Clean up existing database for clean test
    if os.path.exists("academic_twin.db"):
        os.remove("academic_twin.db")
        print("Cleaned up existing database")
    
    # Test 1: Initialize fresh database
    print("\n1. Testing fresh database initialization...")
    from db import init_db
    init_db()
    
    if os.path.exists("academic_twin.db"):
        print("✓ Database file created successfully")
    else:
        print("✗ Database file not created")
        return
    
    # Test 2: Test database logging
    print("\n2. Testing database logging functions...")
    try:
        # Log some test interactions
        log_interaction("integration_test_1", "Kinematics", 60.5, 3.2)
        log_interaction("integration_test_1", "Kinematics", 45.0, 1.5)
        log_interaction("integration_test_2", "Thermodynamics", 120.0, -2.0)
        
        print("✓ Successfully logged 3 test interactions")
        
        # Check database stats
        stats = get_db_stats()
        print(f"  Total interactions: {stats['total_interactions']}")
        print(f"  Unique students: {stats['unique_students']}")
        
    except Exception as e:
        print(f"✗ Database logging failed: {e}")
        return
    
    # Test 3: Test API interaction (if API key available)
    print("\n3. Testing API interaction...")
    try:
        result = interact_with_twin(
            student_id="integration_test_api",
            topic="Kinematics",
            user_input="What is velocity?",
            is_test_active=False
        )
        
        print(f"✓ API call successful")
        print(f"  Mode: {result['mode']}")
        print(f"  Response length: {len(result['response'])}")
        print(f"  New score: {result['new_score']}")
        
        # Log this API interaction
        log_interaction(
            student_id="integration_test_api",
            topic="Kinematics",
            engagement_seconds=30.0,
            score_delta=result['new_score'] - 0.0  # Starting from 0
        )
        print("✓ Logged API interaction to database")
        
    except Exception as e:
        print(f"⚠ API call failed (might be expected if no API key): {str(e)[:100]}")
    
    # Test 4: Verify database contents
    print("\n4. Verifying database contents...")
    try:
        conn = sqlite3.connect("academic_twin.db")
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM interactions")
        total_count = cursor.fetchone()[0]
        print(f"✓ Total interactions in database: {total_count}")
        
        cursor.execute("SELECT student_id, topic, engagement_seconds, score_delta FROM interactions")
        rows = cursor.fetchall()
        
        print("\nSample data:")
        for i, (student_id, topic, engagement, delta) in enumerate(rows[:3], 1):
            print(f"  {i}. {student_id} - {topic}: {engagement}s, Δ{delta}")
        
        conn.close()
    except Exception as e:
        print(f"✗ Database verification failed: {e}")
    
    # Test 5: Test student history retrieval
    print("\n5. Testing student history retrieval...")
    try:
        history = get_student_history("integration_test_1")
        print(f"✓ Retrieved {len(history)} interactions for integration_test_1")
        
        if history:
            latest = history[0]
            print(f"  Latest: {latest['datetime']} - Topic: {latest['topic']}")
            print(f"         Engagement: {latest['engagement_seconds']}s, Score Δ: {latest['score_delta']}")
    
    except Exception as e:
        print(f"✗ History retrieval failed: {e}")
    
    # Test 6: Check database file size
    print("\n6. Database file check...")
    if os.path.exists("academic_twin.db"):
        file_size = os.path.getsize("academic_twin.db")
        print(f"✓ Database file size: {file_size} bytes")
    else:
        print("✗ Database file not found")
    
    print("\n" + "="*60)
    print("Integration test complete!")
    print("="*60)
    
    # Show final database statistics
    print("\nFinal Database Statistics:")
    stats = get_db_stats()
    for key, value in stats.items():
        if key == 'topic_counts':
            print(f"  {key}:")
            for topic, count in value.items():
                print(f"    {topic}: {count}")
        elif key == 'total_engagement_hours':
            print(f"  {key}: {value:.2f} hours")
        else:
            print(f"  {key}: {value}")


if __name__ == "__main__":
    test_integration()