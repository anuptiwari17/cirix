from langchain_google_genai import GoogleGenerativeAIEmbeddings
from app.config import GEMINI_API_KEY

#now i will be using  Gemini's own embedding API. No local model, no torch, no CUDA packages,
# just an API call, keeps the deployed footprint tiny to keep size under 512 for deployment
embedder = GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-001",
    google_api_key=GEMINI_API_KEY,
    output_dimensionality=768,  #fixed dimension so it stays consistent across the app
)