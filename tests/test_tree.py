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


def test_build_tree_respects_max_depth(monkeypatch):
    class DepthDecomposer:
        def decompose(self, char, depth):
            if char == "A":
                return {"components": ["B"]}
            if char == "B":
                return {"components": ["C"]}
            return {"components": []}

    monkeypatch.setattr(tree, "get_decomposer", lambda: DepthDecomposer())

    builder = tree.HanziTreeBuilder(max_depth=1)
    root = tree.HanziNode("A")
    builder.build_tree(root)

    assert [child.character for child in root.children] == ["B"]
    assert root.children[0].children == []


def test_build_tree_stops_on_cycles(monkeypatch):
    class CyclicDecomposer:
        def decompose(self, char, depth):
            if char == "A":
                return {"components": ["B"]}
            if char == "B":
                return {"components": ["A"]}
            return {"components": []}

    monkeypatch.setattr(tree, "get_decomposer", lambda: CyclicDecomposer())

    builder = tree.HanziTreeBuilder(max_depth=5)
    root = tree.HanziNode("A")
    builder.build_tree(root)

    assert [child.character for child in root.children] == ["B"]
    assert root.children[0].children[0].character == "A"
    assert root.children[0].children[0].children == []
