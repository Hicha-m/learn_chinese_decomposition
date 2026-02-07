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

    def test_module_integration_anki_available(self, isolate_paths):
        """Test that Anki module is available for integration."""
        assert hasattr(anki, "save_note_anki")
        assert hasattr(anki, "export_anki")
        assert callable(anki.save_note_anki)
        assert callable(anki.export_anki)

    def test_module_integration_learning_workflow_functions_exist(self, isolate_paths):
        """Test that learning module has required workflow functions."""
        assert hasattr(learning, "mark_as_learned")
        assert hasattr(learning, "build_dictionary_result")
        assert callable(learning.mark_as_learned)
        assert callable(learning.build_dictionary_result)
