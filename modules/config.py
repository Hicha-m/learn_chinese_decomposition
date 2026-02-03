"""
Configuration and constants module.

This module contains all configuration settings, file paths, constants,
and global variables for the Chinese character learning application.

Environment variables required (.env file):
- DIR: Base directory path for data files
- GOOGLE_API_KEY: API key for Google Gemini
- OPENROUTER_API_KEY: API key for OpenRouter
"""

import os
from pathlib import Path
from collections import defaultdict
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

__all__ = [
    'DIR',
    'GOOGLE_API_KEY',
    'OPENROUTER_API_KEY',
    'PATH_DIR',
    'DATA_DIR',
    'HANZI_DIR',
    'ANKI_DIR',
    'WORD_TO_BUBBLES_FILE',
    'BUBBLES_FILE',
    'LEARNED_FILE',
    'RULES_FILE',
    'ANKI_FILE',
    'PINYIN_RULES_FILE',
    'LEARNED_CHARACTERISTIC_FILE',
    'CHARACTERS_TO_LEARN_FILE',
    'CHINESE_MODEL_ID',
    'PINYIN_RULES',
    'PINYIN_ALIASES',
    'RULES',
    'my_path_overrides',
    'my_stops',
    'my_overrides',
    'DEFAULT_PINYIN_RULES',
    'initialize_config',
    'resolve_pinyin_sound',
]

# Load environment variables
DIR = os.getenv('DIR', './')
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')

# Directory paths
PATH_DIR = Path(DIR)
DATA_DIR = Path(f"{DIR}data")  # learned_chars / rules
HANZI_DIR = Path(f"{DIR}hanzi")  # form learning / sentences
ANKI_DIR = Path(f"{DIR}anki")  # anki notes

# File paths
WORD_TO_BUBBLES_FILE = PATH_DIR / "word_to_bulles.json"
BUBBLES_FILE = PATH_DIR / "bubbles.json"
LEARNED_FILE = DATA_DIR / "learned_chars.json"
RULES_FILE = DATA_DIR / "rules.json"
ANKI_FILE = ANKI_DIR / "anki_notes.pkl"
PINYIN_RULES_FILE = DATA_DIR / "pinyin_rules.json"
LEARNED_CHARACTERISTIC_FILE = DATA_DIR / "learned_chars_characteristic.json"
CHARACTERS_TO_LEARN_FILE = DATA_DIR / "characters_to_learn.json"  # Target characters from ##HANZI section

# Anki configuration
CHINESE_MODEL_ID = 1766865029552

# Pinyin rules for mnemonic learning
# Default structure - will be loaded from file if exists
# IMPORTANT: Removed duplicate keys (y/yi, en/n, eng/ng) - use aliases instead
DEFAULT_PINYIN_RULES = {
    "initials": {
        "b": "",    # male
        "p": "",
        "m": "",
        "f": "",
        "d": "",
        "t": "",
        "n": "",
        "l": "",
        "g": "",
        "k": "karim",
        "h": "",
        "zh": "",   # male
        "ch": "",
        "sh": "",
        "r": "",
        "z": "",
        "c": "",
        "s": "",
        "": "",
        "zhi": "",  # male
        "chi": "",
        "shi": "",
        "ri": "",
        "zi": "",
        "ci": "",
        "si": "",
        "y": "",    # female (canonical form - yi is alias)
        "bi": "",
        "pi": "",
        "mi": "",
        "di": "",
        "ti": "",
        "ni": "",
        "li": "",
        "ji": "",
        "qi": "",
        "xi": "",
        "w": "",    # fiction
        "bu": "",
        "pu": "",
        "mu": "",
        "fu": "",
        "du": "",
        "tu": "",
        "nu": "",
        "lu": "",
        "gu": "",
        "ku": "",
        "hu": "",
        "zhu": "",
        "chu": "",
        "shu": "",
        "ru": "",
        "zu": "",
        "cu": "",
        "su": "",
        "yu": "",   # leader world wide
        "nü": "",
        "lü": "",
        "ju": "",
        "qu": "",
        "xu": ""
    },
    "finals": {
        "a": "",
        "ai": "",
        "ao": "",
        "an": "",
        "ang": "",
        "e": "",
        "ei": "",
        "en": "",    # canonical form (n is alias)
        "eng": "",   # canonical form (ng is alias)
        "": "",
        "o": "",
        "ong": "",
        "ou": "trou"
    },
    "tones": {
        "1": "entrance",
        "2": "kitchen/hallway",
        "3": "bedroom/living rooms",
        "4": "bathroom/backyard",
        "5": "roof/basement"
    }
}

# Pinyin sound aliases - different spellings of the same phonetic sound
# These map alternate forms to their canonical forms in PINYIN_RULES
PINYIN_ALIASES = {
    "initials": {
        "yi": "y",      # yi is an alternate spelling of y initial
    },
    "finals": {
        "n": "en",      # n is an alternate spelling of en final
        "ng": "eng",    # ng is an alternate spelling of eng final
    }
}

# Will be populated at runtime from file
PINYIN_RULES = {}
RULES = {}

# Character decomposition rules and overrides
# These are initialized with defaults and can be overridden by RULES from file
my_path_overrides = {
    ('手', '㇒'): '一'
}

my_stops = {'口', '一', '丨', '亅', '丿', '丶', '㇒', '⺊', '丄'}

my_overrides = {'𤴓': '正'}


def initialize_config():
    """
    Initialize runtime configuration by loading from files.
    
    Sets PINYIN_RULES, RULES, and updates decomposition settings from saved files.
    Falls back to defaults if files don't exist.
    
    Note: Call this AFTER config and data are both imported to avoid circular imports.
    """
    global PINYIN_RULES, RULES, my_path_overrides, my_stops, my_overrides
    
    # Lazy import to avoid circular dependency at module load time
    try:
        from . import data
        
        # Load or use defaults
        loaded_pinyin = data.load_pinyin_rules()
        if loaded_pinyin:
            PINYIN_RULES.update(loaded_pinyin)
        else:
            PINYIN_RULES.update(DEFAULT_PINYIN_RULES)
        
        loaded_rules = data.load_rules()
        if loaded_rules:
            RULES.update(loaded_rules)
            
            # Update decomposition rules from RULES if available
            if "path_overrides" in loaded_rules:
                # Convert JSON-serialized keys back to tuples
                import json
                for key_str, value in loaded_rules.get("path_overrides", {}).items():
                    try:
                        key = tuple(json.loads(key_str))
                        my_path_overrides[key] = value
                    except:
                        pass
            
            if "atomic_chars" in loaded_rules:
                my_stops.update(loaded_rules.get("atomic_chars", []))
            
            if "overrides" in loaded_rules:
                my_overrides.update(loaded_rules.get("overrides", {}))
        
        print("✅ Configuration initialized from files")
    except Exception as e:
        print(f"⚠️ Configuration initialization failed: {e}")
        print("   Using default values")
        PINYIN_RULES.update(DEFAULT_PINYIN_RULES)


def resolve_pinyin_sound(sound, category="finals"):
    """
    Resolve a pinyin sound to its canonical form using aliases.
    
    This function handles aliases for equivalent pinyin sounds:
    - 'yi' -> 'y' (initials)
    - 'n' -> 'en' (finals)
    - 'ng' -> 'eng' (finals)
    
    Args:
        sound: The pinyin sound to look up
        category: Either 'initials' or 'finals' (default: 'finals')
    
    Returns:
        The mnemonic/description for the sound, or empty string if not found
    
    Example:
        >>> resolve_pinyin_sound('yi', 'initials')  # Returns: "" (same as 'y')
        >>> resolve_pinyin_sound('n', 'finals')     # Returns: "" (same as 'en')
    """
    if not sound:
        return ""
    
    # Check if it's an alias and resolve to canonical form
    if category == "initials":
        canonical_sound = PINYIN_ALIASES.get("initials", {}).get(sound, sound)
    else:  # finals
        canonical_sound = PINYIN_ALIASES.get("finals", {}).get(sound, sound)
    
    # Look up the canonical sound in PINYIN_RULES
    if category == "initials":
        return PINYIN_RULES.get("initials", {}).get(canonical_sound, "")
    else:  # finals
        return PINYIN_RULES.get("finals", {}).get(canonical_sound, "")
