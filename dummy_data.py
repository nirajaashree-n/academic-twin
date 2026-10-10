"""Dummy data for Academic Twin frontend.

Contains hardcoded credentials and sample responses for the Streamlit UI.
"""

# Hardcoded login credentials
VALID_CREDENTIALS = {
    "student": "1234",
    # Add more dummy users if needed
    # "teacher": "password",
    # "admin": "admin123",
}

# Sample Socratic-style responses for Twin
TWIN_RESPONSES = [
    "What do you already know about this topic?",
    "Can you explain that in more detail?",
    "What evidence supports that idea?",
    "How does this relate to what we've studied before?",
    "What would be a counterargument to that point?",
    "Let's explore this step by step. What's the first thing that comes to mind?",
    "Why do you think that's the case?",
    "What questions does this raise for you?",
    "How could you apply this concept to a real-world situation?",
    "What assumptions are you making here?",
]

# Welcome messages for Twin
WELCOME_MESSAGES = [
    "Hello! I'm A.T., your learning companion.",
    "Ready to explore new topics together?",
    "What would you like to discuss today?",
]

def get_random_response() -> str:
    """Return a random Twin response."""
    import random
    return random.choice(TWIN_RESPONSES)

def get_welcome_message() -> str:
    """Return a welcome message for the Twin."""
    import random
    return random.choice(WELCOME_MESSAGES)

def validate_credentials(username: str, password: str) -> bool:
    """Validate username and password against dummy data.
    
    Args:
        username: Username to validate
        password: Password to validate
        
    Returns:
        True if credentials are valid, False otherwise
    """
    return username in VALID_CREDENTIALS and VALID_CREDENTIALS[username] == password