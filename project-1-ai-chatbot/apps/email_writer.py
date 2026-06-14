# Import required libraries
import streamlit as st       # UI framework
from groq import Groq        # AI API client
from dotenv import load_dotenv  # to read .env file
import os                    # to access environment variables

# Load .env file so GROQ_API_KEY is available
load_dotenv()

# Create Groq client - same as text generator
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# ─── PAGE SETUP ────────────────────────────────────────────
st.set_page_config(page_title="AI Email Writer", page_icon="📧")
st.title("📧 AI Email Writer")
st.write("Generate professional emails instantly.")

# ─── USER INPUTS ───────────────────────────────────────────

# Who is the email going to
recipient = st.text_input("Recipient", placeholder="e.g. My manager, Client, HR team")

# What is the email about
purpose = st.text_input("Purpose", placeholder="e.g. Request for leave, Follow up on meeting")

# Any extra details to include
details = st.text_area("Additional Details", placeholder="e.g. Leave is from Monday to Wednesday, project name, etc.", height=100)

# ─── GENERATE BUTTON ───────────────────────────────────────
if st.button("Generate Email"):

    # Check required fields
    if not recipient or not purpose:
        st.warning("Please fill in Recipient and Purpose.")
    else:
        with st.spinner("Writing your email..."):

            # ── API CALL ───────────────────────────────────
            # Same pattern as text generator
            # Only the system message changes - that's it
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",

                messages=[
                    {
                        "role": "system",
                        # System message sets the AI's job
                        # We tell it exactly what kind of email to write
                        "content": """You are a professional email writer.
                        Write clear, concise, and professional emails.
                        Always include:
                        - A subject line starting with 'Subject:'
                        - A proper greeting
                        - A clear body
                        - A professional sign-off
                        Do not add any explanation outside the email."""
                    },
                    {
                        "role": "user",
                        # User message contains the actual inputs from the form
                        # We combine all 3 inputs into one clear request
                        "content": f"Write a professional email to: {recipient}\nPurpose: {purpose}\nDetails: {details}"
                    }
                ],

                # Low temperature = more consistent, structured output
                # Emails should be predictable, not creative
                temperature=0.5,

                # Enough tokens for a full email
                max_tokens=500
            )

        # ─── DISPLAY RESULT ────────────────────────────────
        generated_email = response.choices[0].message.content

        st.subheader("Your Email:")
        # text_area acts as copy box - user can select all and copy
        st.text_area("Copy from here:", value=generated_email, height=300)