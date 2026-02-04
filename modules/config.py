"""
Configuration and initialization module.

This module contains runtime configuration state and initialization logic
for the Chinese character learning application.

It imports only the values it directly uses, keeping the module focused and clean.
Path constants should be imported directly from constants.py.
"""

from .constants import GOOGLE_API_KEY, OPENROUTER_API_KEY
from .data import load_tree_rules

__all__ = [
    'GOOGLE_API_KEY',
    'OPENROUTER_API_KEY',
    'CHINESE_MODEL_ID',
    'TREE_RULES',
    'initialize_config',
]

# Anki configuration
CHINESE_MODEL_ID = 1766865029552

# Will be populated at runtime from file
TREE_RULES = {}


def initialize_config():
    """
    Initialize runtime configuration by loading tree rules from files.
    
    Sets TREE_RULES and updates decomposition settings from saved files.
    Falls back to defaults if files don't exist.
    """
    # Load or use defaults
    loaded_rules = load_tree_rules()
    TREE_RULES.clear()
    TREE_RULES.update(loaded_rules)
    
    print("✅ Configuration initialized from files")

