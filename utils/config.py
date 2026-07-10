import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
LLM_API_KEY = GROQ_API_KEY or OPENAI_API_KEY
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "https://api.groq.com/openai/v1")
LLM_MODEL = os.getenv("LLM_MODEL", "mixtral-8x7b-32768")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
DATABASE_PATH = os.getenv("DATABASE_PATH", "chatbot_ecommerce.db")
