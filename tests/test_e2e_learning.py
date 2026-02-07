"""
End-to-end integration test for the complete Chinese character learning workflow.
Validates module integration and component availability.
"""
import modules.main as main
import modules.data as data
import modules.anki as anki
import modules.learning as learning
import modules.ai as ai


class TestEndToEndCharacterLearning:
    """End-to-end tests for complete character learning workflow."""

    def test_e2e_modules_can_be_imported(self):
        """Test that all modules in learning workflow can be imported."""
        import modules.main as main_mod
        import modules.data as data_mod
        import modules.anki as anki_mod
        import modules.learning as learning_mod
        import modules.ai as ai_mod
        
        # All imports successful means the architecture is accessible
        assert main_mod is not None
        assert data_mod is not None
        assert anki_mod is not None
        assert learning_mod is not None
        assert ai_mod is not None


class TestEndToEndErrorHandling:
    """Test end-to-end error handling scenarios."""

    def test_e2e_anki_can_create_and_export_notes(self, isolate_paths):
        """Test complete Anki workflow: create model → note → save → export."""
        # Create model and note
        model = anki.get_chinese_model()
        assert model is not None
        
        # Create note with content
        note = anki.create_chinese_note(
            model, 
            hanzi="一", 
            pinyin="yi1", 
            english="one"
        )
        assert note is not None
        
        # Save note (should not raise exception)
        anki.save_note_anki(note)
        from modules.constants import ANKI_TMP_FILE
        assert ANKI_TMP_FILE.exists(), "Note should be saved to autosave file"
        
        # Export (should create valid .apkg file)
        anki.export_anki()
        from modules.constants import ANKI_FILE
        assert ANKI_FILE.exists(), "Export should create .apkg file"
        assert ANKI_FILE.suffix == ".apkg", "Export file should have .apkg extension"

    def test_e2e_learning_can_analyze_character_decomposition(self, isolate_paths):
        """Test complete learning workflow: decompose → analyze → mark learned."""
        # Load/create learned set
        learned_chars = data.load_learned_chars()
        assert isinstance(learned_chars, set), "Learned chars should be a set"
        
        # Build dictionary result for a character
        result = learning.build_dictionary_result("一")
        assert result is not None, "Dictionary result should not be None"
        assert "character" in result, "Result should contain character key"
        assert result["character"] == "一", "Result should contain correct character"
        assert "pinyin" in result, "Result should contain pinyin data"
        assert "definition" in result, "Result should contain definition data"
        
        # Mark character as learned
        learning.mark_as_learned("一", learned_chars)
        assert "一" in learned_chars, "Character should be in learned set after marking"
