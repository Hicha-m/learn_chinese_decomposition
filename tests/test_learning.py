from modules import learning


class DummyDict:
    def get_pinyin(self, char):
        raise RuntimeError("boom")

    def definition_lookup(self, char):
        raise RuntimeError("boom")

    def dictionary_search(self, char):
        raise RuntimeError("boom")


def test_build_dictionary_result_fallback_on_exception():
    result = learning.build_dictionary_result("A", dictionary=DummyDict())

    assert result["character"] == "A"
    assert result["pinyin"] == []
    assert result["definition"] == []
    assert result["search"] is None


def test_learn_character_ready_root_when_dependencies_learned(monkeypatch):
    class SimpleDecomposer:
        def decompose(self, char, depth):
            if char == "A":
                return {"components": ["B"]}
            return {"components": []}

    monkeypatch.setattr(learning.tree, "get_decomposer", lambda: SimpleDecomposer())

    builder = learning.tree.HanziTreeBuilder(max_depth=3)
    learned = {"B"}

    char_to_learn, radicals, status = learning.learn_character("A", builder, learned)

    assert char_to_learn == "A"
    assert radicals == "B"
    assert status == "ok"
