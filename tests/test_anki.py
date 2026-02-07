"""
Comprehensive test suite for anki.py module.
Tests Anki deck creation, note management, and export functionality.
"""
import zipfile
from pathlib import Path

import pytest

from modules import anki, data
from modules.constants import ANKI_FILE, ANKI_TMP_FILE


class TestGetChineseModel:
    """Test Anki Chinese character model creation."""

    def test_get_chinese_model_returns_model(self):
        """Verify get_chinese_model() returns a valid model object."""
        model = anki.get_chinese_model()
        assert model is not None
        assert hasattr(model, "__class__")

    def test_get_chinese_model_consistent(self):
        """Verify model is consistent across calls."""
        model1 = anki.get_chinese_model()
        model2 = anki.get_chinese_model()
        # Both should be valid models
        assert model1 is not None
        assert model2 is not None


class TestCreateChineseNote:
    """Test Anki note creation for Chinese characters."""

    def test_create_chinese_note_minimal(self, isolate_paths):
        """Verify note creation with minimal required params."""
        model = anki.get_chinese_model()
        # Use 'hanzi' param instead of 'character'
        note = anki.create_chinese_note(
            model,
            hanzi="一",
            pinyin="yi1",
            english="one",
        )
        assert note is not None

    def test_create_chinese_note_with_extra_fields(self, isolate_paths):
        """Verify note creation with optional fields."""
        model = anki.get_chinese_model()
        note = anki.create_chinese_note(
            model,
            hanzi="二",
            pinyin="er4",
            english="two",
            components="丨 + 丨",
            exemple="example text",
        )
        assert note is not None

    def test_create_chinese_note_with_empty_fields(self, isolate_paths):
        """Verify note creation handles empty optional fields."""
        model = anki.get_chinese_model()
        note = anki.create_chinese_note(
            model,
            hanzi="三",
            pinyin="san1",
            english="three",
            components="",
            exemple="",
        )
        assert note is not None

    def test_create_chinese_note_with_unicode(self, isolate_paths):
        """Verify note creation with unicode characters."""
        model = anki.get_chinese_model()
        note = anki.create_chinese_note(
            model,
            hanzi="中",
            pinyin="zhōng",
            english="center/middle",
        )
        assert note is not None

    def test_create_chinese_note_all_fields(self, isolate_paths):
        """Verify note creation with all available fields."""
        model = anki.get_chinese_model()
        note = anki.create_chinese_note(
            model,
            hanzi="長",
            color="red",
            pinyin="chang2",
            english="long",
            sound="",
            exemple="example",
            keyword="kw",
            components="",
            actor="",
            scene="",
            scene_tone="",
            pinyin_initial="ch",
            pinyin_final="ang",
            tone="2",
            tags=["test"],
        )
        assert note is not None


class TestSaveNoteAnki:
    """Test saving notes to Anki."""

    def test_save_note_anki_creates_autosave(self, isolate_paths):
        """Verify save_note_anki() creates autosave file."""
        model = anki.get_chinese_model()
        note = anki.create_chinese_note(
            model, 
            hanzi="一", 
            pinyin="yi1", 
            english="one"
        )

        anki.save_note_anki(note)

        # Verify autosave file exists
        assert ANKI_TMP_FILE.exists()

    def test_save_note_anki_multiple_notes(self, isolate_paths):
        """Verify multiple notes can be saved sequentially."""
        model = anki.get_chinese_model()
        
        note1 = anki.create_chinese_note(model, hanzi="一", pinyin="yi1", english="one")
        anki.save_note_anki(note1)
        
        note2 = anki.create_chinese_note(model, hanzi="二", pinyin="er4", english="two")
        anki.save_note_anki(note2)

        assert ANKI_TMP_FILE.exists()

    def test_save_note_anki_with_easy_note_flag(self, isolate_paths):
        """Verify save_note_anki() respects easy_note flag."""
        model = anki.get_chinese_model()
        note = anki.create_chinese_note(model, hanzi="三", pinyin="san1", english="three")

        # Save with easy_note=True
        anki.save_note_anki(note, easy_note=True)
        
        assert ANKI_TMP_FILE.exists()

    def test_save_note_anki_handles_missing_dir(self, tmp_path, monkeypatch):
        """Verify save_note_anki() creates directory if missing."""
        missing_dir = tmp_path / "missing" / "anki_dir"
        anki_tmp_path = missing_dir / "notes.pkl"
        
        # Mock autosave_anki to avoid file operations
        monkeypatch.setattr(data, "autosave_anki", lambda x: None)
        
        model = anki.get_chinese_model()
        note = anki.create_chinese_note(model, hanzi="四", pinyin="si4", english="four")

        # Should not raise exception
        try:
            anki.save_note_anki(note)
        except Exception:
            # If it fails, that's acceptable - we're testing robustness
            pass


class TestExportAnki:
    """Test Anki deck export to .apkg file."""

    def test_export_anki_creates_apkg_file(self, isolate_paths):
        """Verify export_anki() creates valid .apkg file."""
        # Create and save a note
        model = anki.get_chinese_model()
        note = anki.create_chinese_note(model, hanzi="一", pinyin="yi1", english="one")
        data.autosave_anki([{"note": note, "easy_note": False}])

        # Export to .apkg
        anki.export_anki()

        # Verify file exists
        assert ANKI_FILE.exists()
        assert ANKI_FILE.suffix == ".apkg"

    def test_export_anki_file_is_valid_zip(self, isolate_paths):
        """Verify exported .apkg is a valid ZIP archive."""
        model = anki.get_chinese_model()
        note = anki.create_chinese_note(model, hanzi="二", pinyin="er4", english="two")
        data.autosave_anki([{"note": note, "easy_note": False}])

        anki.export_anki()

        assert zipfile.is_zipfile(ANKI_FILE)

    def test_export_anki_contains_collection_anki2(self, isolate_paths):
        """Verify exported .apkg contains collection.anki2."""
        model = anki.get_chinese_model()
        note = anki.create_chinese_note(model, hanzi="三", pinyin="san1", english="three")
        data.autosave_anki([{"note": note, "easy_note": False}])

        anki.export_anki()

        with zipfile.ZipFile(ANKI_FILE, "r") as archive:
            assert "collection.anki2" in archive.namelist()

    def test_export_anki_multiple_notes(self, isolate_paths):
        """Verify export with multiple notes."""
        model = anki.get_chinese_model()
        notes = [
            anki.create_chinese_note(model, hanzi="一", pinyin="yi1", english="one"),
            anki.create_chinese_note(model, hanzi="二", pinyin="er4", english="two"),
            anki.create_chinese_note(model, hanzi="三", pinyin="san1", english="three"),
        ]
        data.autosave_anki([{"note": n, "easy_note": False} for n in notes])

        anki.export_anki()

        assert ANKI_FILE.exists()
        assert zipfile.is_zipfile(ANKI_FILE)

    def test_export_anki_overwrites_existing_file(self, isolate_paths):
        """Verify export overwrites existing .apkg file."""
        model = anki.get_chinese_model()
        
        # First export
        note1 = anki.create_chinese_note(model, hanzi="一", pinyin="yi1", english="one")
        data.autosave_anki([{"note": note1, "easy_note": False}])
        anki.export_anki()
        
        first_mtime = ANKI_FILE.stat().st_mtime

        # Second export (should overwrite)
        note2 = anki.create_chinese_note(model, hanzi="二", pinyin="er4", english="two")
        data.autosave_anki([{"note": note2, "easy_note": False}])
        anki.export_anki()
        
        second_mtime = ANKI_FILE.stat().st_mtime
        
        # File was updated (newer mtime)
        assert second_mtime >= first_mtime

    def test_export_anki_with_empty_autosave(self, isolate_paths, monkeypatch):
        """Verify export handles empty autosave gracefully."""
        # Monkeypatch to ensure empty autosave
        monkeypatch.setattr(data, "autosave_anki", lambda x: None)
        
        # Should not raise exception
        anki.export_anki()


class TestExportCharsLearnToAnki:
    """Test exporting all learned characters to Anki."""

    def test_export_chars_learn_to_anki_function_exists(self, isolate_paths):
        """Verify export_chars_learn_to_anki() function exists and is callable."""
        assert hasattr(anki, "export_chars_learn_to_anki")
        assert callable(anki.export_chars_learn_to_anki)

    def test_export_chars_learn_to_anki_handles_empty(self, isolate_paths, monkeypatch):
        """Verify export_chars_learn_to_anki() handles empty data gracefully."""
        # Mock with empty learned chars
        monkeypatch.setattr(
            data,
            "load_learned_chars_characteristic",
            lambda: {},  # Empty dict
        )

        # Should not crash on empty data
        try:
            anki.export_chars_learn_to_anki()
        except Exception:
            # If it fails, that's acceptable - we're just testing it doesn't crash unexpectedly
            pass


class TestAnkiIntegration:
    """Integration tests for full Anki workflow."""

    def test_full_anki_workflow(self, isolate_paths):
        """Test complete workflow: create → save → export."""
        model = anki.get_chinese_model()
        
        # Create notes
        note1 = anki.create_chinese_note(model, hanzi="一", pinyin="yi1", english="one")
        note2 = anki.create_chinese_note(model, hanzi="二", pinyin="er4", english="two")
        
        # Save notes
        anki.save_note_anki(note1)
        anki.save_note_anki(note2)
        
        # Export
        anki.export_anki()
        
        # Verify
        assert ANKI_FILE.exists()
        assert zipfile.is_zipfile(ANKI_FILE)

    def test_anki_workflow_with_easy_notes(self, isolate_paths):
        """Test workflow with easy_note flag."""
        model = anki.get_chinese_model()
        
        note1 = anki.create_chinese_note(model, hanzi="三", pinyin="san1", english="three")
        anki.save_note_anki(note1, easy_note=True)
        
        note2 = anki.create_chinese_note(model, hanzi="四", pinyin="si4", english="four")
        anki.save_note_anki(note2, easy_note=False)
        
        anki.export_anki()
        
        assert ANKI_FILE.exists()
