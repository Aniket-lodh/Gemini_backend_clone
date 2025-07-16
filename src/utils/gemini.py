import google.generativeai as genai
from src.core.variables import GEMINI_API_KEY

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("models/gemini-1.5-flash")


def call_gemini_api(prompt: str) -> str:
    """
    Calls the Gemini API with the given prompt and returns the response text.
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error: {e}"
