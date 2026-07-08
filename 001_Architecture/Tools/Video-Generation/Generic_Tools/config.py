import os
from pathlib import Path
from dotenv import load_dotenv

# Load from centralized secrets file in home directory
HOME_SECRETS = Path.home() / ".env-secrets"
load_dotenv(HOME_SECRETS)

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
KIE_API_KEY = os.getenv("KIE_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
YOUTUBE_DATA_API_KEY = os.getenv("YOUTUBE_DATA_API_KEY")

if not KIE_API_KEY:
    print("WARNING: KIE_API_KEY is not set. Looking in: ", os.getcwd())
if not ELEVENLABS_API_KEY:
    print("WARNING: ELEVENLABS_API_KEY is not set.")
if not GEMINI_API_KEY:
    print("WARNING: GEMINI_API_KEY / GOOGLE_API_KEY is not set.")
