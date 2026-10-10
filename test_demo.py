# Test script to demonstrate Academic Twin functionality

import dummy_data

print("=== Academic Twin Dummy Data Test ===\n")

# Test 1: Validate credentials
print("1. Testing credential validation:")
print(f"   student/1234: {dummy_data.validate_credentials('student', '1234')}")
print(f"   student/wrong: {dummy_data.validate_credentials('student', 'wrong')}")
print(f"   wrong/1234: {dummy_data.validate_credentials('wrong', '1234')}")

# Test 2: Get welcome messages
print("\n2. Testing welcome messages:")
for i in range(3):
    print(f"   Welcome message {i+1}: {dummy_data.get_welcome_message()}")

# Test 3: Get random Twin responses  
print("\n3. Testing Twin responses:")
for i in range(5):
    print(f"   Response {i+1}: {dummy_data.get_random_response()}")

print("\n=== Application Structure ===")
print("app.py contains:")
print("  - initialize_session_state(): Sets up session state variables")
print("  - login_page(): Renders login form with credential validation")
print("  - chat_page(): Renders chat interface with message history")
print("  - main(): Entry point with authentication routing")

print("\n=== To run the application ===")
print("1. Activate virtual environment")
print("2. Run: streamlit run app.py")
print("3. Use credentials: student / 1234")