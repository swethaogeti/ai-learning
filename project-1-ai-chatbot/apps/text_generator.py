import streamlit as st
from groq import Groq
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

st.set_page_config(page_title="Text Generator", page_icon=":pencil2:")
st.title("Text Generator")
st.write("Generate any text by choosing topic, length and tone")

topic = st.text_input("Topic",placeholder="Enter the topic for text generation:")
tone = st.selectbox("Tone", ["Formal", "Informal", "Humorous", "Serious","Professional"])
length = st.selectbox("Length", ["Short (100 words)", "Medium (200-300 words)", "Long (500+ words)"])

if length == "Short (100 words)":
    max_tokens = 150    # ~100 words
elif length == "Medium (300 words)":
    max_tokens = 400    # ~300 words
else:
    max_tokens = 800    # ~600 words

if st.button("Generate Text"):

        if not topic:
            st.warning("Please enter a topic for text generation.")
        else:
            with st.spinner("Generating text..."):

                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                    {
                        "role": "system",
                        "content": f"You are a content writer. Write in a {tone.lower()} tone. Be concise and engaging."
                        # f-string means the tone variable gets inserted here
                        # If user picked "Funny", this becomes "Write in a funny tone"
                    },
                    {
                        # USER MESSAGE: the actual request
                        "role": "user",
                        "content": f"Write about: {topic}"
                    }
                ],
                    max_tokens=max_tokens,
                    temperature=0.7
                )

                geenrated_text = response.choices[0].message.content
                st.subheader("Generated Text:")
               

                st.text_area("Generated Text", value=geenrated_text, height=300)