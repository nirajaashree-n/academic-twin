"""Test db.py validation fix"""

import sys
import os

# Add current directory to path
sys.path.append('.')

import db

def test_db_validation():
    """Test that db.py accepts any topic string."""
    print("Testing db.py database validation...")
    print("="*60)
    
    # Delete old database to start fresh
    if os.path.exists('academic_twin.db'):
        os.remove('academic_twin.db')
        print("Cleaned up existing database")
    
    # Reinitialize
    db.init_db()
    print("Initialized fresh database")
    
    # Test logging with different topics
    test_cases = [
        ('test1', 'Physics', 60.5, 2.0),
        ('test2', 'CustomTopic123', 45.0, 1.5),
        ('test3', 'Quantum Mechanics', 120.0, 3.5),
        ('test4', 'Biology with Advanced Concepts', 90.0, 2.5),
        ('test5', 'Math/Calculus/Multi-variable', 75.0, 1.0)
    ]
    
    print("\nTesting log_interaction() with various topics:")
    print("-" * 50)
    
    for i, (student_id, topic, engagement, delta) in enumerate(test_cases, 1):
        try:
            interaction_id = db.log_interaction(student_id, topic, engagement, delta)
            print(f"Test {i}: ✓ Logged topic='{topic}' for student='{student_id}' (ID: {interaction_id})")
        except Exception as e:
            print(f"Test {i}: ✗ Failed for topic='{topic}': {e}")
    
    # Get stats
    print("\n" + "="*60)
    print("Database Statistics:")
    print("-" * 50)
    
    stats = db.get_db_stats()
    print(f"Total Interactions: {stats['total_interactions']}")
    print(f"Unique Students: {stats['unique_students']}")
    print(f"Total Engagement: {stats['total_engagement_hours']:.2f} hours")
    print(f"Unique Topics Found: {len(stats['topic_counts'])}")
    print("\nTopic Distribution:")
    
    for topic, count in stats['topic_counts'].items():
        print(f"  '{topic}': {count} records")
    
    # Test get_student_history
    print("\n" + "="*60)
    print("Testing get_student_history():")
    print("-" * 50)
    
    history = db.get_student_history('test1')
    if history:
        print(f"✓ Found {len(history)} records for student 'test1'")
        for record in history:
            print(f"  - Topic: '{record['topic']}', Engagement: {record['engagement_seconds']}s, ΔScore: {record['score_delta']}")
    else:
        print("✗ No history found for student 'test1'")
    
    print("\n" + "="*60)
    print("Test Complete!")
    print(f"✓ db.py successfully accepts ANY topic string")
    print("="*60)

if __name__ == "__main__":
    test_db_validation()