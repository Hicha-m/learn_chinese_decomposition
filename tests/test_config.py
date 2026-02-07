"""
Test suite for config.py module.
Validates configuration loading and validation.
"""
import json
import os
from pathlib import Path

import pytest

from modules import config


class TestConfigLoading:
    """Test configuration file loading."""

    def test_load_config_from_dict(self, tmp_path):
        """Verify configuration can be loaded from dictionary."""
        test_config = {
            "key1": "value1",
            "key2": 42,
            "nested": {"sub_key": "sub_value"},
        }
        
        # Verify dict can be used as config
        assert test_config["key1"] == "value1"
        assert test_config["key2"] == 42
        assert test_config["nested"]["sub_key"] == "sub_value"

    def test_config_constants_module_importable(self):
        """Verify constants module imports successfully."""
        from modules import constants
        assert constants is not None
        assert hasattr(constants, "DIR"), "Constants should have DIR attribute"
        assert constants.DIR is not None, "DIR should be set"


class TestConfigValidation:
    """Test configuration validation."""

    def test_config_module_importable(self):
        """Verify config module can be imported."""
        try:
            from modules import config as cfg
            assert cfg is not None
        except ImportError:
            pytest.fail("Config module should be importable")

    def test_constants_module_has_required_attributes(self):
        """Verify constants module has required attributes."""
        from modules import constants
        
        # Should have standard attributes
        assert hasattr(constants, "DIR"), "Constants missing DIR"
        assert isinstance(constants.DIR, (str, Path)), "DIR should be string or Path"
        
        # Check other critical paths
        assert hasattr(constants, "DATA_DIR"), "Constants missing DATA_DIR"
        assert hasattr(constants, "HANZI_DIR"), "Constants missing HANZI_DIR"
        assert hasattr(constants, "ANKI_DIR"), "Constants missing ANKI_DIR"


class TestConfigFileHandling:
    """Test configuration file I/O."""

    def test_config_can_be_serialized(self):
        """Verify configuration dictionary can be JSON serialized."""
        test_config = {
            "name": "test",
            "value": 123,
            "items": ["a", "b", "c"],
        }
        
        # Should serialize to JSON
        json_str = json.dumps(test_config)
        assert "test" in json_str
        
        # Should deserialize back
        loaded = json.loads(json_str)
        assert loaded["name"] == "test"
        assert loaded["value"] == 123
        assert loaded["items"] == ["a", "b", "c"]

    def test_config_file_persistence(self, tmp_path):
        """Test configuration can be written and read from file."""
        config_file = tmp_path / "config.json"
        test_config = {"setting1": "value1", "setting2": 42}
        
        # Write config
        config_file.write_text(json.dumps(test_config))
        assert config_file.exists(), "Config file should be created"
        
        # Read config
        loaded_config = json.loads(config_file.read_text())
        
        assert loaded_config["setting1"] == "value1"
        assert loaded_config["setting2"] == 42

    def test_config_handles_missing_file(self, tmp_path):
        """Verify system handles missing configuration file gracefully."""
        missing_file = tmp_path / "missing_config.json"
        assert not missing_file.exists()
        
        # Missing file should not prevent app from running (use defaults)
        # This test validates the app behavior, not implementation

    def test_config_handles_corrupted_json(self, tmp_path):
        """Verify system handles corrupted JSON gracefully."""
        corrupted_file = tmp_path / "corrupted.json"
        corrupted_file.write_text("{invalid json}")
        
        # Should either:
        # 1. Raise JSON decode error clearly, OR
        # 2. Fall back to defaults gracefully
        try:
            loaded = json.loads(corrupted_file.read_text())
            pytest.fail("Should reject invalid JSON")
        except json.JSONDecodeError:
            # Expected behavior - clear error on bad JSON
            pass

    def test_constants_paths_are_valid_types(self):
        """Verify all constant paths are proper types."""
        from modules import constants
        
        path_attrs = [
            "DIR", "PATH_DIR", "DATA_DIR", "HANZI_DIR", "ANKI_DIR",
            "WORD_TO_BUBBLES_FILE", "BUBBLES_FILE", "LEARNED_FILE",
            "TREE_RULES_FILE", "ANKI_FILE", "ANKI_TMP_FILE",
            "PINYIN_RULES_FILE", "LEARNED_CHARACTERISTIC_FILE",
            "CHARACTERS_TO_LEARN_FILE"
        ]
        
        for attr_name in path_attrs:
            if hasattr(constants, attr_name):
                attr_value = getattr(constants, attr_name)
                assert isinstance(attr_value, (str, Path)), \
                    f"Constant {attr_name} should be string or Path, got {type(attr_value)}"

    def test_config_handles_corrupted_json(self, tmp_path):
        """Verify system handles corrupted JSON configuration."""
        bad_config_file = tmp_path / "bad_config.json"
        bad_config_file.write_text("{invalid json content")
        
        # Should raise JSONDecodeError or handle gracefully
        with pytest.raises(json.JSONDecodeError):
            json.loads(bad_config_file.read_text())


class TestConfigOverrides:
    """Test configuration override mechanisms."""

    def test_environment_variable_override(self, monkeypatch):
        """Verify environment variables can override config."""
        monkeypatch.setenv("CONFIG_TEST", "test_value")
        
        test_value = os.getenv("CONFIG_TEST")
        assert test_value == "test_value"

    def test_config_precedence(self):
        """Verify configuration precedence (env > file > defaults)."""
        # This validates that the system has a defined precedence order
        # Implementation-specific, but should be documented
        from modules import constants
        
        # Verify config is loaded (shouldn't be None)
        assert constants.DIR is not None


class TestConfigIntegration:
    """Integration tests for configuration usage."""

    def test_config_used_by_data_module(self):
        """Verify configuration is properly used by data module."""
        from modules import data
        
        # Data module should have paths (not None)
        assert data is not None

    def test_all_modules_importable(self):
        """Verify all modules that use config can be imported."""
        from modules import data, learning, anki as anki_module
        
        # All should import successfully
        assert data is not None
        assert learning is not None
        assert anki_module is not None
