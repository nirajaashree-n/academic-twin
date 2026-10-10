"""End-to-end test for Academic Twin with Gemini topic extraction and database logging."""

import sys
import os
import sqlite3
import time

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.services import interact_with_twin
import db


def test_end_to_end():
    """Test the complete flow: Gemini API -> topic extraction -> database logging."""
    print("="*70)
    print("END-TO-END TEST: Academic Twin Integration")
    print("="*70)
    
    # Clean up existing database for clean test
    if os.path.exists("academic_twin.db"):
        os.remove("academic_twin.db")
        print("✓ Cleaned up existing database")
    
    # Initialize fresh database
    db.init_db()
    print("✓ Initialized fresh database")
    
    # Test 1: API call with topic extraction
    print("\n1. Testing API interaction with topic extraction...")
    questions = [
        "What is Newton's second law of motion?",
        "Explain photosynthesis in plants",
        "What is the derivative of x squared?"
    ]
    
    all_passed = True
    
    for i, question in enumerate(questions, 1):
        print(f"\n  Test {i}: '{question}'")
        try:
            response_text, extracted_topic, new_score = interact_with_twin(
                student_id="test_student",
                user_input=question,
                is_test_active=False
            )
            
            # Check if topic was extracted (not "General")
            if extracted_topic != "General":
                print(f"    ✓ Topic extracted: {extracted_topic}")
            else:
                print(f"    ⚠ Topic defaulted to: {extracted_topic}")
            
            # Check response doesn't contain TOPIC line
            if "TOPIC:" not in response_text:
                print(f"    ✓ Response doesn't contain TOPIC line: {len(response_text)} chars")
            else:
                print(f"    ✗ Response still contains TOPIC line")
                all_passed = False
            
            # Check response is not empty
            if response_text and len(response_text) > 10:
                print(f"    ✓ Response is valid: {len(response_text)} chars")
            else:
                print(f"    ✗ Response is too short or empty")
                all_passed = False
            
            # Log to database
            engagement_time = 30.5  # Mock engagement time
            score_delta = new_score - 0.0  # Starting from 0
            
            interaction_id = db.log_interaction(
                student_id="test_student",
                topic=extracted_topic,
                engagement_seconds=engagement_time,
                score_delta=score_delta
            )
            
            print(f"    ✓ Logged to database with ID: {interaction_id}")
            
        except Exception as e:
            print(f"    ✗ Test {i} failed: {str(e)[:100]}")
            all_passed = False
    
    # Test 2: Verify database contents
    print("\n2. Verifying database contents...")
    try:
        history = db.get_student_history("test_student")
        print(f"    ✓ Retrieved {len(history)} interactions for test_student")
        
        if history:
            for i, interaction in enumerate(history[:3], 1):
                print(f"      {i}. Topic: {interaction['topic']}, Engagement: {interaction['engagement_seconds']}s, ΔScore: {interaction['score_delta']}")
        
        # Check database stats
        stats = db.get_db_stats()
        print(f"    ✓ Database stats: {stats['total_interactions']} total interactions")
        print(f"      Topics found: {list(stats['topic_counts'].keys())}")
        
    except Exception as e:
        print(f"    ✗ Database verification failed: {e}")
        all_passed = False
    
    # Test 3: Test with malformed responses
    print("\n3. Testing error handling...")
    try:
        # Test with empty input
        response_text, extracted_topic, new_score = interact_with_twin(
            student_id="test_student_error",
            user_input="",
            is_test_active=False
        )
        
        # Even with empty input, should get some response
        print(f"    ✓ Empty input handled: topic='{extracted_topic}', response_len={len(response_text)}")
        
    except Exception as e:
        print(f"    ⚠ Error with empty input (might be expected): {str(e)[:80]}")
    
    # Test 4: Direct database inspection
    print("\n4. Direct database inspection...")
    try:
        conn = sqlite3.connect("academic_twin.db")
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print(f"    ✓ Tables: {[t[0] for t in tables]}")
        
        cursor.execute("SELECT topic, COUNT(*) FROM interactions GROUP BY topic")
        topic_summary = cursor.fetchall()
        print(f"    ✓ Topics in database: {len(topic_summary)} unique topics")
        
        for topic, count in topic_summary:
            print(f"      - {topic}: {count} records")
        
        conn.close()
    except Exception as e:
        print(f"    ✗ Database inspection failed: {e}")
        all_passed = False
    
    print("\n" + "="*70)
    if all_passed:
        print("✓ ALL TESTS PASSED!")
    else:
        print("⚠ Some tests failed or had warnings")
    print("="*70)
    
    # Show final database state
    print("\nFinal Database State:")
    print("-"*70)
    stats = db.get_db_stats()
    print(f"Total Interactions: {stats['total_interactions']}")
    print(f"Unique Students: {stats['unique_students']}")
    print(f"Total Engagement: {stats['total_engagement_hours']:.2f} hours")
    print(f"Topic Distribution:")
    for topic, count in stats['topic_counts'].items():
        print(f"  {topic}: {count}")
    
    return all_passed


if __name__ == "__main__":
    test_end_to_end()