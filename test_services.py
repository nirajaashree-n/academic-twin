"""Test script for api/services.py"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.services import interact_with_twin, get_system_prompt, STUDENT_SCORES

def test_get_system_prompt():
    """Test the get_system_prompt function."""
    print("Testing get_system_prompt function...")
    
    # Test 1: Normal score
    prompt1 = get_system_prompt("student_1", "Kinematics", 65.0)
    print(f"\nTest 1 - Prompt for score 65.0:")
    print(f"Prompt length: {len(prompt1)}")
    print(f"Contains '65.0/100': {'65.0/100' in prompt1}")
    print(f"Contains '75.0/100': {'75.0/100' in prompt1}")  # 65 + 10 = 75
    print(f"Contains 'Kinematics': {'Kinematics' in prompt1}")
    
    # Test 2: High score (should cap at 100)
    prompt2 = get_system_prompt("student_1", "Calculus", 95.0)
    print(f"\nTest 2 - Prompt for score 95.0:")
    print(f"Contains '95.0/100': {'95.0/100' in prompt2}")
    print(f"Contains '105.0/100': {'105.0/100' in prompt2}")  # Should be False
    print(f"Contains '100.0/100': {'100.0/100' in prompt2}")  # Should be True (capped)
    
    # Test 3: Low score
    prompt3 = get_system_prompt("student_1", "Physics", 10.0)
    print(f"\nTest 3 - Prompt for score 10.0:")
    print(f"Contains '10.0/100': {'10.0/100' in prompt3}")
    print(f"Contains '20.0/100': {'20.0/100' in prompt3}")  # 10 + 10 = 20
    
    print("\n✓ get_system_prompt tests completed")


def test_interact_with_twin():
    """Test the interact_with_twin function."""
    print("\n" + "="*50)
    print("Testing interact_with_twin function...")
    
    # Test 1: Learning mode with existing student
    print("\nTest 1: Learning mode with student_1 and Kinematics")
    try:
        result = interact_with_twin(
            student_id="student_1",
            topic="Kinematics",
            user_input="What is kinematics?",
            is_test_active=False
        )
        print(f"Result mode: {result['mode']}")
        print(f"Response type: {type(result['response'])}")
        print(f"Response length: {len(result['response']) if result['response'] else 0}")
        print(f"First 500 chars of response: {result['response'][:500] if result['response'] else 'N/A'}")
        print(f"Score delta: {result['new_score'] - 65.0:.1f}")
        print(f"New score: {result['new_score']}")
        print(f"Updated STUDENT_SCORES: {STUDENT_SCORES['student_1']['Kinematics']}")
        print("\n=== ACTUAL RESPONSE FROM GEMINI ===")
        print(result['response'])
        print("=== END RESPONSE ===")
        print("✓ Test 1 passed")
    except Exception as e:
        print(f"✗ Test 1 failed: {e}")
        print(f"Error type: {type(e).__name__}")
    
    # Test 2: Learning mode with new student
    print("\nTest 2: Learning mode with new student and new topic")
    try:
        result = interact_with_twin(
            student_id="new_student",
            topic="Calculus",
            user_input="Explain derivatives",
            is_test_active=False
        )
        print(f"Result mode: {result['mode']}")
        print(f"Response type: {type(result['response'])}")
        print(f"New score: {result['new_score']}")
        print(f"Updated STUDENT_SCORES for new_student: {'Calculus' in STUDENT_SCORES.get('new_student', {})}")
        print("✓ Test 2 passed")
    except Exception as e:
        print(f"✗ Test 2 failed: {e}")
        print(f"Error type: {type(e).__name__}")
    
    # Test 3: Test mode
    print("\nTest 3: Test mode")
    try:
        result = interact_with_twin(
            student_id="student_1",
            topic="Thermodynamics",
            user_input="What is entropy?",
            is_test_active=True
        )
        print(f"Result mode: {result['mode']}")
        print(f"Response: {result['response']}")
        print(f"New score: {result['new_score']}")
        print("✓ Test 3 passed")
    except Exception as e:
        print(f"✗ Test 3 failed: {e}")
        print(f"Error type: {type(e).__name__}")
    
    # Test 4: Check environment variable
    print("\nTest 4: Checking API key configuration")
    try:
        from dotenv import load_dotenv
        load_dotenv()
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key:
            print(f"API key loaded: {api_key[:10]}...")
            print("✓ API key found")
        else:
            print("✗ API key not found in .env file")
            print("Please set GEMINI_API_KEY in your .env file")
    except Exception as e:
        print(f"✗ Error checking API key: {e}")
    
    # Summary
    print("\n" + "="*50)
    print("Test Summary:")
    print(f"Total tests attempted: 4")
    print(f"Current STUDENT_SCORES state: {STUDENT_SCORES}")

if __name__ == "__main__":
    test_get_system_prompt()
    test_interact_with_twin()
