import json
from google import genai
from google.genai import types

client = genai.Client()
MODEL_ID = "gemini-2.5-flash"

def generate_pre_visit_summary(symptoms: str) -> dict:
    prompt = f"Analyse these symptoms and return: urgency level (Low / Medium / High), chief complaint, and three suggested questions for the doctor. Symptoms: {symptoms}"
    try:
        response = client.models.generate_content(
            model=MODEL_ID,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                system_instruction="You are a clinical assistant AI. Always output valid JSON with keys: urgency, chief_complaint, and questions (array of strings)."
            )
        )
        return json.loads(response.text)
    except Exception as e:
        print(f"LLM Pre-visit summary error: {str(e)}")
        return {
            "urgency": "Medium",
            "chief_complaint": symptoms[:100],
            "questions": [
                "When did these symptoms first start?",
                "Have you tried any home remedies or medications?",
                "Are these symptoms constant or do they come and go?"
            ]
        }

def generate_post_visit_summary(notes: str) -> str:
    prompt = f"Convert these clinical notes into a patient-friendly summary with medication schedule and follow-up steps: {notes}"
    try:
        response = client.models.generate_content(
            model=MODEL_ID,
            contents=prompt
        )
        return response.text
    except Exception as e:
        print(f"LLM Post-visit summary error: {str(e)}")
        return f"Post-Visit Summary: Your doctor reviewed your condition. Please follow the prescribed medication schedule provided directly in your notes."
