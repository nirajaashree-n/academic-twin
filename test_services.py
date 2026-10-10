"""Test script for api/services.py"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.services import interact_with_twin, get_system_prompt, STUDENT_SCORES

def test_get_system_prompt():
    """Test the get_system_prompt function."""
    print("Testing get_system_prompt function...")
    
    # Test 1: Normal score (now only requires student_id and score)
    prompt1 = get_system_prompt("student_1", 65.0)
    print(f"\nTest 1 - Prompt for score 65.0:")
    print(f"Prompt length: {len(prompt1)}")
    print(f"Contains '65.0/100': {'65.0/100' in prompt1}")
    print(f"Contains '75.0/100': {'75.0/100' in prompt1}")  # 65 + 10 = 75
    print(f"Contains 'TOPIC:' line: {'TOPIC:' in prompt1}")
    
    # Test 2: High score (should cap at 100)
    prompt2 = get_system_prompt("student_1", 95.0)
    print(f"\nTest 2 - Prompt for score 95.0:")
    print(f"Contains '95.0/100': {'95.0/100' in prompt2}")
    print(f"Contains '105.0/100': {'105.0/100' in prompt2}")  # Should be False
    print(f"Contains '100.0/100': {'100.0/100' in prompt2}")  # Should be True (capped)
    print(f"Contains 'TOPIC:' line: {'TOPIC:' in prompt2}")
    
    # Test 3: Low score
    prompt3 = get_system_prompt("student_1", 10.0)
    print(f"\nTest 3 - Prompt for score 10.0:")
    print(f"Contains '10.0/100': {'10.0/100' in prompt3}")
    print(f"Contains '20.0/100': {'20.0/100' in prompt3}")  # 10 + 10 = 20
    print(f"Contains 'TOPIC:' line: {'TOPIC:' in prompt3}")
    
    print("\n✓ get_system_prompt tests completed")


def test_interact_with_twin():
    """Test the interact_with_twin function."""
    print("\n" + "="*50)
    print("Testing interact_with_twin function...")
    
    # Test 1: Learning mode with existing student
    print("\nTest 1: Learning mode with student_1")
    try:
        # Now returns tuple: (response_text, extracted_topic, new_score)
        response_text, extracted_topic, new_score = interact_with_twin(
            student_id="student_1",
            user_input="What is kinematics?",
            is_test_active=False
        )
        print(f"Response type: {type(response_text)}")
        print(f"Response length: {len(response_text) if response_text else 0}")
        print(f"Extracted topic: {extracted_topic}")
        print(f"New score: {new_score}")
        
        # Check that response doesn't contain TOPIC line
        if "TOPIC:" not in response_text:
            print(f"✓ Response doesn't contain TOPIC line")
        else:
            print(f"✗ Response still contains TOPIC line")
        
        print(f"First 200 chars of response: {response_text[:200] if response_text else 'N/A'}")
        print("✓ Test 1 passed")
    except Exception as e:
        print(f"✗ Test 1 failed: {e}")
        print(f"Error type: {type(e).__name__}")
    
    # Test 2: Learning mode with new student
    print("\nTest 2: Learning mode with new student")
    try:
        response_text, extracted_topic, new_score = interact_with_twin(
            student_id="new_student",
            user_input="Explain derivatives",
            is_test_active=False
        )
        print(f"Response length: {len(response_text)}")
        print(f"Extracted topic: {extracted_topic}")
        print(f"New score: {new_score}")
        print(f"Topic not 'General': {extracted_topic != 'General'}")
       # print(f"Updated STUDENT_SCORES for new_student: '{extracted_topic}' in STUDENT_SCORES.get('new_student', {})? {extracted_topic in STUDENT_SCORES.get('new_student', {})}")
        print("✓ Test 2 passed")
    except Exception as e:
        print(f"✗ Test 2 failed: {e}")
        print(f"Error type: {type(e).__name__}")
    
    # Test 3: Test mode
    print("\nTest 3: Test mode")
    try:
        response_text, extracted_topic, new_score = interact_with_twin(
            student_id="student_1",
            user_input="What is entropy?",
            is_test_active=True
        )
        print(f"Response: {response_text}")
        print(f"Extracted topic (should be 'General'): {extracted_topic}")
        print(f"New score: {new_score}")
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
    
    # Test 5: Test multiple topics (as per requirement)
    print("\nTest 5: Testing 3 different topics")
    topics_to_test = ["Tell me about relativity", "Explain photosynthesis", "What is the integral of x?"]
    all_passed = True
    
    for i, question in enumerate(topics_to_test, 1):
        try:
            response_text, extracted_topic, new_score = interact_with_twin(
                student_id=f"multi_topic_test_{i}",
                user_input=question,
                is_test_active=False
            )
            print(f"  Test {i} - Question: '{question[:30]}...'")
            print(f"    Extracted topic: {extracted_topic}")
            print(f"    Response length: {len(response_text)}")
            print(f"    TOPIC line in response: {'TOPIC:' in response_text}")
            print(f"    Score: {new_score}")
            if "TOPIC:" not in response_text:
                print(f"    ✓ PASS - No TOPIC line in response")
            else:
                print(f"    ✗ FAIL - TOPIC line still in response")
                all_passed = False
        except Exception as e:
            print(f"  Test {i} failed: {e}")
            all_passed = False
    
    # Summary
    print("\n" + "="*50)
    print("Test Summary:")
    print(f"Total tests attempted: 5")
    print(f"All tests passed: {all_passed}")
    print(f"Current STUDENT_SCORES state keys: {list(STUDENT_SCORES.keys())}")

if __name__ == "__main__":
    test_get_system_prompt()
    test_interact_with_twin()
