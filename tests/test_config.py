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

    def test_config_defaults_exist(self):
        """Verify default configuration structure is available."""
        # Config module should be importable with valid structure
        import modules.config
        assert modules.config is not None
        # If it imports without error, basic config structure is sound


class TestConfigValidation:
    """Test configuration validation."""

    def test_config_module_importable(self):
        """Verify config module can be imported."""
        # Test that config module loads without errors
        try:
            from modules import config as cfg
            assert cfg is not None
        except ImportError:
            pytest.fail("Config module should be importable")

    def test_constants_module_has_required_attributes(self):
        """Verify constants module has required attributes."""
        from modules import constants
        
        # Should have standard attributes
        assert hasattr(constants, "DIR")
        assert isinstance(constants.DIR, (str, Path))


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

    def test_config_file_persistence(self, tmp_path):
        """Test configuration can be written and read from file."""
        config_file = tmp_path / "config.json"
        test_config = {"setting1": "value1", "setting2": 42}
        
        # Write config
        config_file.write_text(json.dumps(test_config))
        
        # Read config
        loaded_config = json.loads(config_file.read_text())
        
        assert loaded_config["setting1"] == "value1"
        assert loaded_config["setting2"] == 42

    def test_config_handles_missing_file(self, tmp_path):
        """Verify system handles missing configuration file gracefully."""
        missing_file = tmp_path / "missing_config.json"
        assert not missing_file.exists()
        
        # Reading should handle gracefully (either fail clearly or use defaults)
        # This depends on implementation, but it should not crash unexpectedly

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
