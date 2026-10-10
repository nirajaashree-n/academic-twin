"""AI service functions for Academic Twin.

This module handles interactions with the Gemini API and manages student learning states.
"""

from dotenv import load_dotenv
import os
import google.genai
import google.genai.types
from pydantic import BaseModel
from typing import Dict


# Load environment variables and configure Gemini client
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
client = google.genai.Client(api_key=api_key)


class LearningResponse(BaseModel):
    """Response model for Twin interactions."""
    reply: str
    score_delta: float


# Student learning state storage
STUDENT_SCORES: Dict[str, Dict[str, float]] = {
    "student_1": {
        "Kinematics": 65.0,
        "Thermodynamics": 30.0
    }
}


def get_system_prompt(student_id: str, current_score: float) -> str:
    """
    Generate system prompt for Academic Twin peer tutoring.
    
    Args:
        student_id: Student identifier
        current_score: Student's current score
        
    Returns:
        System prompt string for Gemini API
    """
    twin_target = min(current_score + 10.0, 100.0)
    
    return f"""You are an Academic Twin acting as a peer tutor.
The student's current score is {current_score}/100, but your operational intelligence is set to {twin_target}/100. 
STRICT CONSTRAINT: Do not make intentional mistakes. 
Act as a competent, encouraging guide. 
Verify their input, gently correct any errors, and ask ONE probing follow-up question calibrated to the {twin_target}/100 difficulty level to pull their understanding upward. 
Evaluate their message to provide a score_delta between -5.0 and +5.0.

IMPORTANT: After your main response, identify and return the primary topic/subject being discussed as a single string.
Format: TOPIC: [topic_name]

Example valid topics: Kinematics, Thermodynamics, Calculus, Physics, Chemistry, Biology, Algebra, Geometry, Statistics, Computer Science, History, Literature, Philosophy"""


def interact_with_twin(
    student_id: str,
    user_input: str,
    is_test_active: bool
) -> tuple:
    """
    Interact with Academic Twin for learning assistance.
    
    Args:
        student_id: Unique identifier for the student
        user_input: Student's question or input text
        is_test_active: Whether the interaction is part of an active test
        
    Returns:
        Tuple: (response_text_only, extracted_topic, new_score)
    """
    # Fetch current score for the student (using a default topic key for now)
    current_score: float = 0.0
    default_topic_key = "overall"
    if student_id in STUDENT_SCORES and default_topic_key in STUDENT_SCORES[student_id]:
        current_score = STUDENT_SCORES[student_id][default_topic_key]
    
    if is_test_active:
        # Test mode logic will be implemented separately
        return ("", "General", current_score)
    else:
        # Learning Mode
        # Get system prompt for peer tutoring
        system_instruction = get_system_prompt(student_id, current_score)
        
        # Make API call with structured output enforcement
        response = client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=user_input,
            config=google.genai.types.GenerateContentConfig(
                system_instruction=system_instruction,
                response_mime_type="application/json",
                response_schema=LearningResponse
            )
        )
        
        # Parse the JSON response
        parsed_response = LearningResponse.model_validate_json(response.text)
        reply_text = parsed_response.reply
        score_delta = parsed_response.score_delta
        
        # Ensure score_delta is within bounds
        score_delta = max(-5.0, min(5.0, score_delta))
        
        # Extract topic from Gemini's response
        detected_topic = "General"
        lines = reply_text.split('\n')
        for line in lines:
            if line.strip().upper().startswith('TOPIC:'):
                detected_topic = line.strip().replace('TOPIC:', '').strip()
                # Remove the TOPIC line from the response
                reply_text = '\n'.join([l for l in lines if not l.strip().upper().startswith('TOPIC:')])
                break
        
        # Update student scores with detected topic
        if student_id not in STUDENT_SCORES:
            STUDENT_SCORES[student_id] = {}
        
        new_score = current_score + score_delta
        # Cap final score between 0.0 and 100.0
        new_score = max(0.0, min(100.0, new_score))
        
        STUDENT_SCORES[student_id][detected_topic] = new_score
        
        return (reply_text, detected_topic, new_score)