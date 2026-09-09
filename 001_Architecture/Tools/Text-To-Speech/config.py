"""Runtime configuration for the shared ElevenLabs TTS utility."""

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path.home() / ".env-secrets")
ELEVENLABS_API_KEY = os.environ.get("ELEVENLABS_API_KEY", "")
