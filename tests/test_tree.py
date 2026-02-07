from modules import tree


class FakeDecomposer:
    def decompose(self, char, depth):
        if char == "A":
            return {"components": ["B", "C"]}
        if char == "B":
            return {"components": ["D"]}
        return {"components": [char]}


def test_analyze_character_v3_ready_logic(monkeypatch):
    monkeypatch.setattr(tree, "get_decomposer", lambda: FakeDecomposer())

    builder = tree.HanziTreeBuilder(
        overrides={},
        path_overrides={},
        atomic_chars=set(),
        max_depth=3,
    )
    learned = {"C", "D"}

    result = tree.analyze_character_v3("A", builder, learned)

    assert result["required_radicals"] == ["B"]
    assert result["known_radicals"] == ["C", "D"]
    assert result["ready"] == ["B"]
