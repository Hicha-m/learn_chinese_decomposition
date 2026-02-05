"""
Constants and environment configuration module.

This module contains all static path constants and environment variables
for the Chinese character learning application.

This module has NO dependencies on other application modules, only stdlib + dotenv.
This makes it safe to import from anywhere without circular dependency risks.

Environment variables required (.env file):
- DIR: Base directory path for data files
- GOOGLE_API_KEY: API key for Google Gemini
- OPENROUTER_API_KEY: API key for OpenRouter
"""

import os
from pathlib import Path
from dotenv import load_dotenv

__all__ = [
    # Environment variables
    'DIR',
    'GOOGLE_API_KEY',
    'OPENROUTER_API_KEY',
    
    # Directory paths
    'PATH_DIR',
    'DATA_DIR',
    'HANZI_DIR',
    'ANKI_DIR',
    
    # File paths
    'WORD_TO_BUBBLES_FILE',
    'BUBBLES_FILE',
    'LEARNED_FILE',
    'TREE_RULES_FILE',
    'ANKI_FILE',
    'PINYIN_RULES_FILE',
    'LEARNED_CHARACTERISTIC_FILE',
    'CHARACTERS_TO_LEARN_FILE',
]

# Load environment variables from .env file
load_dotenv()

# Environment variables
DIR = os.getenv('DIR', './')
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')

# Directory paths
PATH_DIR = Path(DIR)
DATA_DIR = Path(f"{DIR}data")  # learned_chars / rules
HANZI_DIR = Path(f"{DIR}hanzi")  # form learning / sentences
ANKI_DIR = Path(f"{DIR}anki")  # anki notes

# File paths
WORD_TO_BUBBLES_FILE = DATA_DIR / "word_to_bulles.json"
BUBBLES_FILE = DATA_DIR / "bubbles.json"
LEARNED_FILE = DATA_DIR / "learned_chars.json"
TREE_RULES_FILE = DATA_DIR / "rules.json"
ANKI_FILE = ANKI_DIR / "mandarin_chinese.apkg"
ANKI_TMP_FILE = ANKI_DIR / "anki_notes.pkl"
PINYIN_RULES_FILE = DATA_DIR / "pinyin_rules.json"
LEARNED_CHARACTERISTIC_FILE = DATA_DIR / "learned_chars_characteristic.json"
CHARACTERS_TO_LEARN_FILE = DATA_DIR / "characters_to_learn.json"  # Target characters from ##HANZI section
