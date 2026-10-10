"""Academic Twin - Streamlit Frontend

A minimalist, professional chat interface with login and dummy responses.
No backend, no real AI, no database - just mock data and UI components.
"""

import streamlit as st
import time
from typing import List, Dict, Optional
import dummy_data
from api.services import interact_with_twin
import db


def initialize_session_state():
    """Initialize all session state variables."""
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    
    if "username" not in st.session_state:
        st.session_state.username = ""
    
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    
    if "initialized_welcome" not in st.session_state:
        st.session_state.initialized_welcome = False
    
    if "message_count" not in st.session_state:
        st.session_state.message_count = 0
    
    if "current_topic" not in st.session_state:
        st.session_state.current_topic = "Kinematics"
    
    if "engagement_start_time" not in st.session_state:
        st.session_state.engagement_start_time = None
    
    if "engagement_paused_time" not in st.session_state:
        st.session_state.engagement_paused_time = None
    
    if "total_engagement_seconds" not in st.session_state:
        st.session_state.total_engagement_seconds = 0
    
    if "current_score" not in st.session_state:
        st.session_state.current_score = 0.0


def update_engagement_time():
    """Update engagement time tracking."""
    current_time = time.time()
    
    # Start engagement timer on first message
    if st.session_state.engagement_start_time is None and st.session_state.chat_history:
        st.session_state.engagement_start_time = current_time
    
    # Check if idle for more than 2 minutes (120 seconds)
    if st.session_state.chat_history:
        last_message_time = st.session_state.chat_history[-1].get("timestamp", 0)
        if current_time - last_message_time > 120:
            if st.session_state.engagement_paused_time is None:
                st.session_state.engagement_paused_time = current_time
        else:
            # Resume if paused
            if st.session_state.engagement_paused_time is not None:
                paused_duration = current_time - st.session_state.engagement_paused_time
                st.session_state.total_engagement_seconds += paused_duration
                st.session_state.engagement_paused_time = None
    
    # Calculate total engagement time
    if st.session_state.engagement_start_time is not None:
        if st.session_state.engagement_paused_time is None:
            # Currently active
            active_duration = current_time - st.session_state.engagement_start_time
            total_time = st.session_state.total_engagement_seconds + active_duration
        else:
            # Currently paused
            total_time = st.session_state.total_engagement_seconds
    
    return total_time if 'total_time' in locals() else 0


def login_page():
    """Render the login page with username/password form."""
    st.set_page_config(page_title="Academic Twin - Login", page_icon="🎓")
    
    st.title("🎓 Academic Twin")
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.subheader("Login")
        
        with st.form("login_form"):
            username = st.text_input("Username", placeholder="Enter your username", help="")
            password = st.text_input("Password", type="password", placeholder="Enter your password", help="")
            submit_button = st.form_submit_button("Login")
            
            if submit_button:
                if username and password:
                    if dummy_data.validate_credentials(username, password):
                        st.session_state.authenticated = True
                        st.session_state.username = username
                        st.session_state.chat_history = []
                        st.session_state.message_count = 0
                        st.success(f"Welcome, {username}!")
                        st.rerun()
                    else:
                        st.error("Invalid username or password. Try: student / 1234")
                else:
                    st.warning("Please enter both username and password")
        
        st.info("Demo credentials: **student** / **1234**")
    
    st.markdown("---")
    st.caption("Academic Twin - Your AI Learning Companion")


def chat_page():
    """Render the chat interface page."""
    st.set_page_config(page_title="Academic Twin - Chat", page_icon="🤖", layout="wide")
    
    st.title("🤖 Chat with Academic Twin")
    st.markdown(f"**Logged in as:** {st.session_state.username}")
    st.markdown("---")
    
    # Display chat history with styling
    if st.session_state.chat_history:
        for message in st.session_state.chat_history:
            if message["role"] == "user":
                # Student message - right aligned blue
                st.markdown(
                    f"""<div style='background-color: #e3f2fd; padding: 10px; border-radius: 10px; 
                    margin: 5px; text-align: right; border-left: 5px solid #2196f3;'>
                    <strong>You:</strong> {message["content"]}
                    </div>""",
                    unsafe_allow_html=True
                )
            else:
                # Twin response - left aligned gray
                st.markdown(
                    f"""<div style='background-color: #f5f5f5; padding: 10px; border-radius: 10px; 
                    margin: 5px; text-align: left; border-left: 5px solid #9e9e9e;'>
                    <strong>Academic Twin:</strong> {message["content"]}
                    </div>""",
                    unsafe_allow_html=True
                )
    else:
        st.info("No messages yet. Start a conversation!")
    
    st.markdown("---")
    
    # Chat input controls
    with st.form("chat_form"):
        col1, col2, col3 = st.columns([3, 1, 1])
        
        with col1:
            user_input = st.text_area(
                "Type your message here...",
                key=f"chat_input_{st.session_state.message_count}",
                label_visibility="collapsed",
                placeholder="Ask a question or discuss a topic... (Press Enter to send, Shift+Enter for new line)",
                height=38
            )
        
        with col2:
            send_button = st.form_submit_button("📤 Send", use_container_width=True, type="primary")
        
        with col3:
            voice_button = st.form_submit_button("🎤 Voice", use_container_width=True)
            if voice_button:
                st.write("voice input triggered")
    
    # Handle form submission (either Enter key or button click)
    if send_button and user_input:
        # Update engagement time before logging
        total_engagement = update_engagement_time()
        
        # Add timestamp to user message
        user_timestamp = time.time()
        
        # Append student message to chat history with timestamp
        st.session_state.chat_history.append({
            "role": "user",
            "content": user_input,
            "timestamp": user_timestamp
        })
        
        # Track previous score for delta calculation
        previous_score = st.session_state.current_score
        
        # Call Academic Twin API
        try:
            result = interact_with_twin(
                student_id="student_1",  # Using fixed student ID for now
                topic=st.session_state.current_topic,
                user_input=user_input,
                is_test_active=False  # Always learning mode for now
            )
            
            twin_response = result["response"]
            st.session_state.current_score = result["new_score"]
            
            # Append Twin's response with timestamp
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": twin_response,
                "timestamp": time.time()
            })
            
            # Calculate score delta
            score_delta = st.session_state.current_score - previous_score
            
        except Exception as e:
            # Fallback to dummy response if API fails
            twin_response = f"API Error: {str(e)[:100]}... Using dummy response: {dummy_data.get_random_response()}"
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": twin_response,
                "timestamp": time.time()
            })
            score_delta = 0.0
        
        # Log interaction to database
        try:
            db.log_interaction(
                student_id="student_1",
                topic=st.session_state.current_topic,
                engagement_seconds=total_engagement,
                score_delta=score_delta
            )
            
            # Reset engagement metrics after logging
            st.session_state.engagement_start_time = None
            st.session_state.engagement_paused_time = None
            st.session_state.total_engagement_seconds = 0
            
        except Exception as e:
            st.warning(f"Failed to log interaction: {str(e)[:100]}")
        
        # Increment message count to clear the input field
        st.session_state.message_count += 1
        
        # Clear input and rerun
        st.rerun()
    
    # Clear Chat button
    if st.button("🗑️ Clear Chat", type="secondary"):
        st.session_state.chat_history = []
        st.session_state.initialized_welcome = False
        st.session_state.message_count = 0
        st.rerun()
    
    # Logout button
    st.markdown("---")
    if st.button("🚪 Logout", type="primary"):
        st.session_state.authenticated = False
        st.session_state.username = ""
        st.session_state.chat_history = []
        st.session_state.initialized_welcome = False
        st.session_state.message_count = 0
        st.session_state.engagement_start_time = None
        st.session_state.engagement_paused_time = None
        st.session_state.total_engagement_seconds = 0
        st.session_state.current_score = 0.0
        st.rerun()


def main():
    """Main application entry point."""
    initialize_session_state()
    
    # Apply custom styling
    st.markdown("""
    <style>
        .stApp { max-width: 1200px; margin: 0 auto; }
        .stButton button { border-radius: 8px; padding: 8px 16px; }
        #MainMenu, footer, header { visibility: hidden; }
    </style>
    """, unsafe_allow_html=True)
    
    # Authentication routing
    if not st.session_state.authenticated:
        login_page()
    else:
        # Show welcome message if not initialized
        if not st.session_state.initialized_welcome:
            welcome_msg = dummy_data.get_welcome_message()
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": welcome_msg
            })
            st.session_state.initialized_welcome = True
            st.rerun()
        
        chat_page()


if __name__ == "__main__":
    main()