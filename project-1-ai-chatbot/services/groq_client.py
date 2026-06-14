# Groq client lives here
# Every app imports the client from this file
# This means the client is created ONCE, not copy-pasted in every file

from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()  # load .env file

def get_client():
    # Creates and returns the Groq client
    # Called like: client = get_client()
    return Groq(api_key=os.getenv("GROQ_API_KEY"))