"""Global configuration for literature_claw."""

import os
from pathlib import Path
from dotenv import load_dotenv

# Project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"
PAPERS_DIR = DATA_DIR / "papers"
SUMMARIES_DIR = DATA_DIR / "summaries"
OUTPUT_DIR = DATA_DIR / "output"

# Ensure directories exist
for d in (PAPERS_DIR, SUMMARIES_DIR, OUTPUT_DIR):
    d.mkdir(parents=True, exist_ok=True)

# Load environment variables
load_dotenv(PROJECT_ROOT / ".env")

# LLM configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "gpt-4o")

# Supported models
AVAILABLE_MODELS = {
    "gpt-4o": "openai/gpt-4o",
    "gpt-4o-mini": "openai/gpt-4o-mini",
    "claude-sonnet-4-20250514": "anthropic/claude-sonnet-4-20250514",
    "claude-haiku-3-5": "anthropic/claude-3-5-haiku-20241022",
}
