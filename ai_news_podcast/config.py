"""Central configuration. Everything here can be overridden with environment variables."""
import os
from pathlib import Path

# Models
ROOT_MODEL = os.getenv("ROOT_AGENT_MODEL", "gemini-2.5-flash-native-audio-preview-09-2025")
PODCASTER_MODEL = os.getenv("PODCASTER_AGENT_MODEL", "gemini-2.5-flash")
TTS_MODEL = os.getenv("TTS_MODEL", "gemini-2.5-flash-preview-tts")

# Where the report (.md) and podcast (.wav) are written
OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", "outputs"))

# Podcast hosts -> Gemini prebuilt voices
HOST_VOICES = {"Joe": "Kore", "Jane": "Puck"}

# Guardrail configuration
WHITELIST_DOMAINS = [
    "techcrunch.com",
    "venturebeat.com",
    "theverge.com",
    "technologyreview.com",
    "arstechnica.com",
]

BLOCKED_DOMAINS = [
    "wikipedia.org",     # general info, not latest news
    "reddit.com",        # discussion forum, not primary news
    "youtube.com",       # video, not useful for text processing
    "medium.com",        # blog platform with variable quality
    "investopedia.com",  # financial definitions, not tech news
    "quora.com",         # Q&A site, opinions not reports
]
