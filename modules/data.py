"""
Data loading and saving module.

This module handles all file I/O operations for:
- Character learning progress
- Pinyin rules
- Character characteristics
- Anki notes persistence
- Word to bubbles mapping
"""

import json
import pickle
from pathlib import Path
from collections import defaultdict

from . import config

__all__ = [
    'save',
    'load_word_to_bubbles',
    'load_bubbles',
    'save_learned_chars',
    'save_rules',
    'save_hanzi',
    'save_pinyin_rules',
    'save_learned_chars_characteristic',
    'autosave_anki',
    'load_learned_chars',
    'load_pinyin_rules',
    'load_learned_chars_characteristic',
    'load_rules',
    'autoload_anki',
]


def save(dir, text):
    """Save text to file."""
    with open(dir, "w", encoding="utf-8") as f:
        f.write(text)


def load_word_to_bubbles():
    """Load word to bubbles mapping from JSON file."""
    if not config.WORD_TO_BUBBLES_FILE.exists():
        print(f"{config.WORD_TO_BUBBLES_FILE} not exist !")
        d = {}
        save(config.WORD_TO_BUBBLES_FILE, str(d))
        return d
    with open(config.WORD_TO_BUBBLES_FILE, "r", encoding="utf-8") as f:
        loaded_word_to_bulles_dict = json.load(f)
    word_to_bubbles = defaultdict(set)
    for word, bulle_indices_list in loaded_word_to_bulles_dict.items():
        word_to_bubbles[word].update(bulle_indices_list)
    return word_to_bubbles


def load_bubbles():
    """Load bubbles list from JSON file."""
    if not config.BUBBLES_FILE.exists():
        print(f"{config.BUBBLES_FILE} not exist !")
        l = []
        save(config.BUBBLES_FILE, str(l))
        return l
    with open(config.BUBBLES_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_learned_chars(learned_chars):
    """Save learned characters set to JSON file."""
    config.DATA_DIR.mkdir(exist_ok=True)
    data = {
        "learned": sorted(set(learned_chars))
    }
    with open(config.LEARNED_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def save_rules(atomic_chars, overrides, path_overrides):
    """Save decomposition rules to JSON file."""
    config.DATA_DIR.mkdir(exist_ok=True)
    # Convert tuple keys to JSON-serializable format
    serializable_path_overrides = {
        json.dumps(key, ensure_ascii=False): value
        for key, value in path_overrides.items()
    }
    
    data = {
        "atomic_chars": sorted(set(atomic_chars)),
        "overrides": overrides,
        "path_overrides": serializable_path_overrides
    }
    with open(config.RULES_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def save_hanzi(char, text, name):
    """Save hanzi character data to file."""
    config.HANZI_DIR.mkdir(exist_ok=True)
    file_path = config.HANZI_DIR / f"{char}_{name}.txt"
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(text)


def save_pinyin_rules(pinyin_rules):
    """Save pinyin rules to JSON file."""
    config.DATA_DIR.mkdir(exist_ok=True)
    with open(config.PINYIN_RULES_FILE, "w", encoding="utf-8") as f:
        json.dump(pinyin_rules, f, ensure_ascii=False, indent=4)


def save_learned_chars_characteristic(learned_chars_characteristic):
    """Save learned character characteristics to JSON file."""
    config.DATA_DIR.mkdir(exist_ok=True)
    with open(config.LEARNED_CHARACTERISTIC_FILE, "w", encoding="utf-8") as f:
        json.dump(learned_chars_characteristic, f, ensure_ascii=False, indent=4)


def autosave_anki(notes):
    """Auto-save Anki notes to pickle file."""
    config.ANKI_DIR.mkdir(exist_ok=True)
    with open(config.ANKI_FILE, "wb") as f:
        pickle.dump(notes, f)


def load_learned_chars():
    """Load learned characters from JSON file."""
    if not config.LEARNED_FILE.exists():
        return set()
    with open(config.LEARNED_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    return set(data.get("learned", []))


def load_pinyin_rules():
    """Load pinyin rules from JSON file."""
    if not config.PINYIN_RULES_FILE.exists():
        return config.DEFAULT_PINYIN_RULES.copy()
    with open(config.PINYIN_RULES_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def load_learned_chars_characteristic():
    """Load learned character characteristics from JSON file."""
    if not config.LEARNED_CHARACTERISTIC_FILE.exists():
        return {}
    with open(config.LEARNED_CHARACTERISTIC_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def load_rules():
    """Load decomposition rules from JSON file."""
    if not config.RULES_FILE.exists():
        return {
            "atomic": [],
            "overrides": {},
            "path_overrides": {},
        }
    with open(config.RULES_FILE, "r", encoding="utf-8") as f:
        rules = json.load(f)
    return rules


def autoload_anki():
    """Auto-load Anki notes from pickle file."""
    if not config.ANKI_FILE.exists():
        return []
    with open(config.ANKI_FILE, "rb") as f:
        return pickle.load(f)
