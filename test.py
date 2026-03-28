from google import genai
import os
from dotenv import load_dotenv

load_dotenv()

# Ensure your .env has GOOGLE_API_KEY=your_key
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

try:
    response = client.models.generate_content(
        model='gemini-2.5-flash', # Or 'gemini-1.5-flash-latest'
        contents='Say "Gemini is online!"'
    )
    print(response.text)
except Exception as e:
    print(f"Gemini Error: {e}")