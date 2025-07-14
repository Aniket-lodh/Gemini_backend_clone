from collections import deque
import os
from dotenv import load_dotenv

load_dotenv(override=True)

## App ##
HOST = os.getenv("HOST", "localhost")
PORT = int(os.getenv("PORT", "8000"))
JWT_SECRET = os.getenv("JWT_SECRET", "default_fallback_jwt_secret")

## DATABASE ##
DATABASE_HOST = os.getenv("DATABASE_HOST", "localhost")
DATABASE_PORT = os.getenv("DATABASE_PORT", "5432")
DATABASE_DB = os.getenv("DATABASE_DB", "gemini_backend_clone")
DATABASE_USER = os.getenv("DATABASE_USER", "postgres")
DATABASE_PASS = os.getenv("DATABASE_PASS", "")
DATABASE_URL = f"postgresql://{DATABASE_USER}:{DATABASE_PASS}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_DB}"
## LLM ##
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")

## REDIS ##
REDIS_HOST = os.getenv("REDIS_HOST", "")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", None)
REDIS_URL = f"redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/0"

origins = [
    "http://localhost",
    "https://localhost",
    "http://localhost:3000",
    "https://localhost:3000",
    "http://127.0.0.1:3000",
    "https://127.0.0.1:3000",
    "http://localhost:5000",
    "https://localhost:5000",
    "http://localhost:8000",
    "https://localhost:8000",
    "http://localhost:8080",
    "https://localhost:8080",
    "https://localhost:8108",
    "http://127.0.0.1:5173",
    "http://localhost:5173",
]
