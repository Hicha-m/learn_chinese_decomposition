"""
Data loading and saving module.

This module handles all file I/O operations for:
- Character learning progress
- Pinyin rules
- Character characteristics
- Anki notes persistence
- Word to bubbles mapping

It imports path constants from constants.py to avoid circular dependencies.
"""

import json
import pickle
import copy
from collections import defaultdict
import log

from .constants import (
    WORD_TO_BUBBLES_FILE,
    BUBBLES_FILE,
    LEARNED_FILE,
    TREE_RULES_FILE,
    ANKI_TMP_FILE,
    PINYIN_RULES_FILE,
    LEARNED_CHARACTERISTIC_FILE,
    DATA_DIR,
    HANZI_DIR,
    ANKI_DIR,
)

__all__ = [
    'save',
    'load_word_to_bubbles',
    'load_bubbles',
    'save_learned_chars',
    'save_hanzi',
    'save_pinyin_rules',
    'save_learned_chars_characteristic',
    'autosave_anki',
    'load_learned_chars',
    'load_pinyin_rules',
    'load_learned_chars_characteristic',
    'load_tree_rules',
    'autoload_anki',
    'DEFAULT_PINYIN_RULES',
    'DEFAULT_TREE_RULES'
]


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
        "yi": "",   # canonical form (alias: y)
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

DEFAULT_TREE_RULES = {
    "path_overrides": {
        ('手', '㇒'): '一'
    },
    "atomic": {'口', '一', '丨', '亅', '丿', '丶', '㇒', '⺊', '丄'},
    "overrides": {'𤴓': '正'}    
}


def _merge_defaults(defaults, loaded):
    """
    Merge loaded configuration with defaults.
    
    Validates the loaded configuration and warns about unexpected keys or invalid types.
    This maintains forward compatibility by keeping defaults even when loaded JSON differs.
    
    Args:
        defaults: Dictionary of default values
        loaded: Dictionary loaded from JSON file
        
    Returns:
        Merged dictionary with defaults updated by loaded values
    """
    if not isinstance(loaded, dict):
        print(f"⚠️  Warning: Loaded configuration is not a dictionary (type: {type(loaded).__name__}), using defaults")
        return copy.deepcopy(defaults)
    
    merged = copy.deepcopy(defaults)
    
    # Check for unexpected keys
    unexpected_keys = set(loaded.keys()) - set(defaults.keys())
    if unexpected_keys:
        print(f"⚠️  Warning: Unexpected keys in loaded configuration: {unexpected_keys}")
    
    for key, value in loaded.items():
        if key not in defaults:
            # Still add it but warn
            merged[key] = value
            continue
            
        default_value = defaults.get(key)
        
        # For sets, try to convert if we get a list
        if isinstance(default_value, set):
            if isinstance(value, (list, set)):
                merged[key] = set(value)
            else:
                print(f"⚠️  Warning: Key '{key}' expected set/list but got {type(value).__name__}, using default")
                merged[key] = default_value
        # For tuples in dicts (like path_overrides), special handling BEFORE generic dict merge
        elif isinstance(default_value, dict) and key == "path_overrides" and isinstance(value, dict):
            # Convert string keys back to tuples if needed
            converted = {}
            for k, v in value.items():
                if isinstance(k, str) and k.startswith('('):
                    # This is a serialized tuple, eval safely
                    try:
                        k = eval(k)
                    except:
                        print(f"⚠️  Warning: Could not parse tuple key '{k}', skipping")
                        continue
                converted[k] = v
            merged[key].update(converted)
        # For nested dicts, merge recursively
        elif isinstance(value, dict) and isinstance(default_value, dict):
            merged[key].update(value)
        else:
            merged[key] = value
    
    return merged


def _safe_load_json(filepath):
    """
    Safely load JSON from file.
    
    Args:
        filepath: Path object to JSON file
        
    Returns:
        Loaded JSON data or None if parsing fails
    """
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, TypeError) as exc:
        print(f"⚠️  Warning: Failed to parse JSON: {exc}")
        return None


def save(dir, text):
    """Save text to file."""
    with open(dir, "w", encoding="utf-8") as f:
        f.write(text)


def load_word_to_bubbles():
    """Load word to bubbles mapping from JSON file."""
    if not WORD_TO_BUBBLES_FILE.exists():
        print(f"{WORD_TO_BUBBLES_FILE} not exist !")
        d = {}
        save(WORD_TO_BUBBLES_FILE, str(d))
        return d
    with open(WORD_TO_BUBBLES_FILE, "r", encoding="utf-8") as f:
        loaded_word_to_bulles_dict = json.load(f)
    word_to_bubbles = defaultdict(set)
    for word, bulle_indices_list in loaded_word_to_bulles_dict.items():
        word_to_bubbles[word].update(bulle_indices_list)
    return word_to_bubbles


def load_bubbles():
    """Load bubbles list from JSON file."""
    if not BUBBLES_FILE.exists():
        print(f"{BUBBLES_FILE} not exist !")
        l = []
        save(BUBBLES_FILE, str(l))
        return l
    with open(BUBBLES_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_learned_chars(learned_chars):
    """Save learned characters set to JSON file."""
    DATA_DIR.mkdir(exist_ok=True)
    data = {
        "learned": sorted(set(learned_chars))
    }
    with open(LEARNED_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)




def save_hanzi(char, text, name):
    """Save hanzi character data to file."""
    HANZI_DIR.mkdir(exist_ok=True)
    file_path = HANZI_DIR / f"{char}_{name}.md"
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(text)
        log.info(f"Saved in {file_path}")


def save_pinyin_rules(pinyin_rules):
    """Save pinyin rules to JSON file."""
    DATA_DIR.mkdir(exist_ok=True)
    with open(PINYIN_RULES_FILE, "w", encoding="utf-8") as f:
        json.dump(pinyin_rules, f, ensure_ascii=False, indent=4)


def save_learned_chars_characteristic(learned_chars_characteristic):
    """Save learned character characteristics to JSON file."""
    DATA_DIR.mkdir(exist_ok=True)
    with open(LEARNED_CHARACTERISTIC_FILE, "w", encoding="utf-8") as f:
        json.dump(learned_chars_characteristic, f, ensure_ascii=False, indent=4)


def autosave_anki(notes):
    """Auto-save Anki notes to pickle file."""
    ANKI_DIR.mkdir(exist_ok=True)
    with open(ANKI_TMP_FILE, "wb") as f:
        pickle.dump(notes, f)


def load_learned_chars():
    """Load learned characters from JSON file."""
    if not LEARNED_FILE.exists():
        return set()
    
    data = _safe_load_json(LEARNED_FILE)
    if not isinstance(data, dict):
        print(f"⚠️  Warning: Expected dict, using empty set ${LEARNED_FILE}")
        return set()
    
    learned = data.get("learned", [])
    if not isinstance(learned, (list, set, tuple)):
        print("⚠️  Warning: 'learned' is not a list, using empty set")
        return set()
    
    return set(learned)


def load_pinyin_rules():
    """Load pinyin rules from JSON file."""
    if not PINYIN_RULES_FILE.exists():
        return copy.deepcopy(DEFAULT_PINYIN_RULES)
    with open(PINYIN_RULES_FILE, "r", encoding="utf-8") as f:
        loaded = json.load(f)
    return _merge_defaults(DEFAULT_PINYIN_RULES, loaded)


def load_learned_chars_characteristic():
    """Load learned character characteristics from JSON file."""
    if not LEARNED_CHARACTERISTIC_FILE.exists():
        return {}
    with open(LEARNED_CHARACTERISTIC_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def load_tree_rules():
    """Load decomposition rules from JSON file."""
    if not TREE_RULES_FILE.exists():
        return copy.deepcopy(DEFAULT_TREE_RULES)

    with open(TREE_RULES_FILE, "r", encoding="utf-8") as f:
        loaded = json.load(f)
    return _merge_defaults(DEFAULT_TREE_RULES, loaded) # because 


def autoload_anki():
    """Auto-load Anki notes from pickle file."""
    if not ANKI_TMP_FILE.exists():
        return []
    with open(ANKI_TMP_FILE, "rb") as f:
        return pickle.load(f)
