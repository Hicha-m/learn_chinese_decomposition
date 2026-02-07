from modules import data


def test_merge_defaults_path_overrides_tuple(patch_paths):
    defaults = data.DEFAULT_TREE_RULES
    loaded = {"path_overrides": {"('A','B')": "C"}}

    merged = data._merge_defaults(defaults, loaded)

    assert ("A", "B") in merged["path_overrides"]
    assert merged["path_overrides"][("A", "B")] == "C"


def test_load_learned_chars_corrupt_json(patch_paths):
    data.LEARNED_FILE.write_text("{", encoding="utf-8")

    learned = data.load_learned_chars()

    assert learned == set()


def test_load_learned_chars_missing_file(patch_paths, tmp_path, monkeypatch):
    missing = tmp_path / "learned_chars.json"
    monkeypatch.setattr(data, "LEARNED_FILE", missing)

    assert data.load_learned_chars() == set()


def test_load_learned_chars_valid_json(patch_paths, tmp_path, monkeypatch):
    file_path = tmp_path / "learned_chars.json"
    file_path.write_text('{"learned": ["A", "B"]}', encoding="utf-8")
    monkeypatch.setattr(data, "LEARNED_FILE", file_path)

    assert data.load_learned_chars() == {"A", "B"}
