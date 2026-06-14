# Import required libraries
import streamlit as st
from groq import Groq
from dotenv import load_dotenv
import os

# Load .env file
load_dotenv()

# Create Groq client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# ─── PAGE SETUP ────────────────────────────────────────────
st.set_page_config(page_title="AI Blog Generator", page_icon="📝")
st.title("📝 AI Blog Post Generator")
st.write("Generate SEO-optimized blog posts instantly.")

# ─── USER INPUTS ───────────────────────────────────────────

# What the blog is about
topic = st.text_input("Blog Topic", placeholder="e.g. Benefits of morning workout")

# SEO keyword - this is what Google will rank the blog for
# We pass this to AI so it uses the keyword naturally throughout the blog
keyword = st.text_input("Target SEO Keyword", placeholder="e.g. morning workout benefits")

# Audience helps AI adjust the writing style
audience = st.selectbox("Target Audience", ["General", "Beginners", "Professionals", "Students"])

# Length selection
length = st.selectbox("Length", ["Short (300 words)", "Medium (600 words)", "Long (1000 words)"])

# Map length to max_tokens - same pattern as text generator
if length == "Short (300 words)":
    max_tokens = 400
elif length == "Medium (600 words)":
    max_tokens = 800
else:
    max_tokens = 1300

# ─── GENERATE BUTTON ───────────────────────────────────────
if st.button("Generate Blog Post"):

    if not topic or not keyword:
        st.warning("Please fill in Topic and SEO Keyword.")
    else:
        with st.spinner("Writing your blog post..."):

            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",

                messages=[
                    {
                        "role": "system",
                        # SEO instructions in system message
                        # We tell AI exactly how to structure an SEO blog
                        "content": """You are an expert SEO blog writer.
                        Always structure the blog like this:
                        - Title (H1): include the keyword
                        - Introduction: hook the reader, mention keyword naturally
                        - 3-4 sections with subheadings (H2)
                        - Conclusion with a call to action
                        
                        SEO rules to follow:
                        - Use the keyword naturally 3-4 times
                        - Write short paragraphs (3-4 lines max)
                        - Use simple, clear language
                        - Do not stuff the keyword unnaturally"""
                    },
                    {
                        "role": "user",
                        # We pass all 3 user inputs dynamically
                        "content": f"Write an SEO blog post about: {topic}\nTarget keyword: {keyword}\nTarget audience: {audience}"
                    }
                ],

                # 0.7 = creative but structured, good for blogs
                temperature=0.7,
                max_tokens=max_tokens
            )

        # ─── DISPLAY RESULT ────────────────────────────────
        blog_post = response.choices[0].message.content

        st.subheader("Your Blog Post:")
        # markdown renders the headings and formatting properly
        st.markdown(blog_post)

        # Copy box below
        st.text_area("Copy from here:", value=blog_post, height=400)