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


def get_system_prompt(student_id: str, topic: str, current_score: float) -> str:
    """
    Generate system prompt for Academic Twin peer tutoring.
    
    Args:
        student_id: Student identifier
        topic: Learning topic
        current_score: Student's current score on this topic
        
    Returns:
        System prompt string for Gemini API
    """
    twin_target = min(current_score + 10.0, 100.0)
    
    return f"""You are an Academic Twin acting as a peer tutor in '{topic}'. 
The student's current score is {current_score}/100, but your operational intelligence is set to {twin_target}/100. 
STRICT CONSTRAINT: Do not make intentional mistakes. 
Act as a competent, encouraging guide. 
Verify their input, gently correct any errors, and ask ONE probing follow-up question calibrated to the {twin_target}/100 difficulty level to pull their understanding upward. 
Evaluate their message to provide a score_delta between -5.0 and +5.0."""


def interact_with_twin(
    student_id: str,
    topic: str,
    user_input: str,
    is_test_active: bool
) -> Dict:
    """
    Interact with Academic Twin for learning assistance.
    
    Args:
        student_id: Unique identifier for the student
        topic: Learning topic/subject area
        user_input: Student's question or input text
        is_test_active: Whether the interaction is part of an active test
        
    Returns:
        Dictionary containing Twin's response and score information
    """
    # Fetch current score for the student and topic
    current_score: float = 0.0
    if student_id in STUDENT_SCORES and topic in STUDENT_SCORES[student_id]:
        current_score = STUDENT_SCORES[student_id][topic]
    
    if is_test_active:
        # Test mode logic will be implemented separately
        return {"mode": "test", "response": "", "new_score": current_score}
    else:
        # Learning Mode
        # Get system prompt for peer tutoring
        system_instruction = get_system_prompt(student_id, topic, current_score)
        
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
        
        # Update student scores
        if student_id not in STUDENT_SCORES:
            STUDENT_SCORES[student_id] = {}
        
        new_score = current_score + score_delta
        # Cap final score between 0.0 and 100.0
        new_score = max(0.0, min(100.0, new_score))
        
        STUDENT_SCORES[student_id][topic] = new_score
        
        return {
            "mode": "learning",
            "response": reply_text,
            "new_score": new_score
        }