# Streaming Chatbot - Industrial Grade
# Uses config/settings.py for all configuration
# Uses services/groq_client.py for the AI client

import streamlit as st
import sys
import os

# This tells Python to look for modules from the project root
# Without this, "from services..." would fail when running from apps/ folder
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.groq_client import get_client   # import client from services
from config.settings import MODEL, TEMPERATURE, MAX_TOKENS  # import config

# ─── PAGE SETUP ────────────────────────────────────────────
st.set_page_config(
    page_title="AI Chat",
    page_icon="💬",
    layout="centered"
)

# ─── CUSTOM CSS ────────────────────────────────────────────
# This is what separates a toy from a real product
# We override Streamlit's default styles with clean professional ones
st.markdown("""
    <style>
        /* Hide Streamlit default header and footer */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}

        /* Clean background */
        .stApp {
            background-color: #0f0f0f;
        }

        /* Chat input styling */
        .stChatInput input {
            background-color: #1e1e1e;
            border: 1px solid #333;
            border-radius: 12px;
            color: #fff;
        }

        /* User message bubble */
        [data-testid="stChatMessageContent"] {
            border-radius: 12px;
        }

        /* Title styling */
        h1 {
            font-size: 1.5rem !important;
            font-weight: 600 !important;
            color: #ffffff !important;
        }

        /* Muted subtitle */
        .subtitle {
            color: #666;
            font-size: 0.85rem;
            margin-top: -15px;
            margin-bottom: 20px;
        }
    </style>
""", unsafe_allow_html=True)

# ─── HEADER ────────────────────────────────────────────────
st.title("AI Assistant")
st.markdown('<p class="subtitle">Powered by Llama 3.3 · Streaming</p>', unsafe_allow_html=True)

# ─── SESSION STATE ─────────────────────────────────────────
# Persists chat history across reruns
# Also tracks if AI is currently generating (for loading state)
if "messages" not in st.session_state:
    st.session_state.messages = []

if "is_generating" not in st.session_state:
    st.session_state.is_generating = False

# ─── CLEAR CHAT BUTTON ─────────────────────────────────────
if st.session_state.messages:  # only show if there are messages
    if st.button("Clear chat", type="secondary"):
        st.session_state.messages = []
        st.rerun()  # refresh the page to clear UI

# ─── DISPLAY CHAT HISTORY ──────────────────────────────────
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# ─── CHAT INPUT ────────────────────────────────────────────
user_input = st.chat_input(
    "Message AI Assistant...",
    disabled=st.session_state.is_generating  # disable input while AI is typing
)

if user_input:

    # Mark as generating — disables input until AI finishes
    st.session_state.is_generating = True

    # Show user message
    with st.chat_message("user"):
        st.write(user_input)

    # Save to history
    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    # ─── STREAMING RESPONSE ────────────────────────────────
    with st.chat_message("assistant"):

        # Show a status indicator while connecting to AI
        with st.status("Thinking...", expanded=False) as status:
            status.update(label="Generating response...", state="running")

            try:
                # Create Groq client from services/
                client = get_client()

                # API call with stream=True
                stream = client.chat.completions.create(
                    model=MODEL,           # from config/settings.py
                    temperature=TEMPERATURE,
                    max_tokens=MAX_TOKENS,

                    messages=[
                        {
                            "role": "system",
                            "content": "You are a helpful, concise AI assistant. Give clear and direct answers."
                        },
                        # Send full chat history for context
                        *st.session_state.messages
                    ],
                    stream=True  # word by word streaming
                )

                # Stream response word by word into UI
                full_response = st.write_stream(stream)

                # Update status to done
                status.update(label="Done", state="complete")

            except Exception as e:
                # Handle errors gracefully — never show raw errors to user
                st.error("Something went wrong. Please try again.")
                full_response = None
                status.update(label="Error", state="error")

    # Save AI response to history
    if full_response:
        st.session_state.messages.append({
            "role": "assistant",
            "content": full_response
        })

    # Done generating — re-enable input
    st.session_state.is_generating = False
    st.rerun()