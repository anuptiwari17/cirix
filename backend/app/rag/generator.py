from google import genai
from app.config import GEMINI_API_KEY, LLM_MODEL_NAME

client = genai.Client(api_key=GEMINI_API_KEY)


def generate_answer(prompt: str) -> str:
    response = client.models.generate_content(
        model=LLM_MODEL_NAME,
        contents=prompt,
    )
    return response.text