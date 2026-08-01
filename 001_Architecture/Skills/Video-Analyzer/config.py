import os
from pathlib import Path
from dotenv import load_dotenv

HOME_SECRETS = Path.home() / ".env-secrets"
load_dotenv(HOME_SECRETS)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")

if not GEMINI_API_KEY:
    print("WARNING: GEMINI_API_KEY / GOOGLE_API_KEY is not set.")
