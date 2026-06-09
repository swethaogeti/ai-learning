import os
from google import genai
from dotenv import load_dotenv
from typing import Generator

# Load environment variables safely
load_dotenv()

# Initialize the industrial standard client
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def generate_cloud_response(messages: list) -> Generator:
    """
    Industrial Standard: Cleans and streams inputs to the Google GenAI SDK,
    fixing the Pydantic type validation issues.
    """
    try:
        # Instead of formatting dictionaries manually, the simplest 
        # production way to get a quick response is passing the latest prompt string,
        # or passing a clean text context block.
        latest_user_prompt = messages[-1]["content"] if messages else "Hi"

        # Request a streaming response from the fast, free flash model
        response = client.models.generate_content_stream(
            model='gemini-2.5-flash',
            contents=latest_user_prompt,
        )
        
        for chunk in response:
            if chunk.text:
                yield chunk.text
                
    except Exception as e:
        yield f"Cloud API Error: Failed to fetch response. Details: {str(e)}"