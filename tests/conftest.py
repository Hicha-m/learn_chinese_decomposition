from pathlib import Path

import pytest

from modules import constants, data
import modules.anki as anki
import modules.main as main


@pytest.fixture()
def patch_paths(tmp_path, monkeypatch):
    base = tmp_path / "root"
    base.mkdir()

    dir_str = base.as_posix() + "/"
    path_dir = Path(dir_str)
    data_dir = path_dir / "data"
    hanzi_dir = path_dir / "hanzi"
    anki_dir = path_dir / "anki"

    data_dir.mkdir()
    hanzi_dir.mkdir()
    anki_dir.mkdir()

    monkeypatch.setattr(constants, "DIR", dir_str, raising=False)
    monkeypatch.setattr(constants, "PATH_DIR", path_dir, raising=False)
    monkeypatch.setattr(constants, "DATA_DIR", data_dir, raising=False)
    monkeypatch.setattr(constants, "HANZI_DIR", hanzi_dir, raising=False)
    monkeypatch.setattr(constants, "ANKI_DIR", anki_dir, raising=False)
    monkeypatch.setattr(
        constants, "WORD_TO_BUBBLES_FILE", data_dir / "word_to_bulles.json", raising=False
    )
    monkeypatch.setattr(constants, "BUBBLES_FILE", data_dir / "bubbles.json", raising=False)
    monkeypatch.setattr(constants, "LEARNED_FILE", data_dir / "learned_chars.json", raising=False)
    monkeypatch.setattr(constants, "TREE_RULES_FILE", data_dir / "rules.json", raising=False)
    monkeypatch.setattr(constants, "ANKI_FILE", anki_dir / "mandarin_chinese.apkg", raising=False)
    monkeypatch.setattr(constants, "ANKI_TMP_FILE", anki_dir / "anki_notes.pkl", raising=False)
    monkeypatch.setattr(
        constants, "PINYIN_RULES_FILE", data_dir / "pinyin_rules.json", raising=False
    )
    monkeypatch.setattr(
        constants,
        "LEARNED_CHARACTERISTIC_FILE",
        data_dir / "learned_chars_characteristic.json",
        raising=False,
    )
    monkeypatch.setattr(
        constants, "CHARACTERS_TO_LEARN_FILE", data_dir / "characters_to_learn.json", raising=False
    )

    monkeypatch.setattr(data, "DATA_DIR", data_dir, raising=False)
    monkeypatch.setattr(data, "HANZI_DIR", hanzi_dir, raising=False)
    monkeypatch.setattr(data, "ANKI_DIR", anki_dir, raising=False)
    monkeypatch.setattr(data, "WORD_TO_BUBBLES_FILE", constants.WORD_TO_BUBBLES_FILE, raising=False)
    monkeypatch.setattr(data, "BUBBLES_FILE", constants.BUBBLES_FILE, raising=False)
    monkeypatch.setattr(data, "LEARNED_FILE", constants.LEARNED_FILE, raising=False)
    monkeypatch.setattr(data, "TREE_RULES_FILE", constants.TREE_RULES_FILE, raising=False)
    monkeypatch.setattr(data, "ANKI_TMP_FILE", constants.ANKI_TMP_FILE, raising=False)
    monkeypatch.setattr(data, "PINYIN_RULES_FILE", constants.PINYIN_RULES_FILE, raising=False)
    monkeypatch.setattr(
        data, "LEARNED_CHARACTERISTIC_FILE", constants.LEARNED_CHARACTERISTIC_FILE, raising=False
    )


@pytest.fixture()
def isolate_paths(monkeypatch, tmp_path):
    base = tmp_path / "app"
    data_dir = base / "data"
    hanzi_dir = base / "hanzi"
    anki_dir = base / "anki"

    data_dir.mkdir(parents=True, exist_ok=True)
    hanzi_dir.mkdir(parents=True, exist_ok=True)
    anki_dir.mkdir(parents=True, exist_ok=True)

    monkeypatch.setattr(main, "DATA_DIR", data_dir)
    monkeypatch.setattr(main, "HANZI_DIR", hanzi_dir)
    monkeypatch.setattr(main, "ANKI_DIR", anki_dir)

    monkeypatch.setattr(data, "DATA_DIR", data_dir)
    monkeypatch.setattr(data, "HANZI_DIR", hanzi_dir)
    monkeypatch.setattr(data, "ANKI_DIR", anki_dir)
    monkeypatch.setattr(data, "WORD_TO_BUBBLES_FILE", data_dir / "word_to_bulles.json")
    monkeypatch.setattr(data, "BUBBLES_FILE", data_dir / "bubbles.json")
    monkeypatch.setattr(data, "LEARNED_FILE", data_dir / "learned_chars.json")
    monkeypatch.setattr(data, "TREE_RULES_FILE", data_dir / "rules.json")
    monkeypatch.setattr(data, "ANKI_TMP_FILE", anki_dir / "anki_notes.pkl")
    monkeypatch.setattr(data, "PINYIN_RULES_FILE", data_dir / "pinyin_rules.json")
    monkeypatch.setattr(
        data,
        "LEARNED_CHARACTERISTIC_FILE",
        data_dir / "learned_chars_characteristic.json",
    )

    monkeypatch.setattr(anki, "ANKI_FILE", anki_dir / "mandarin_chinese.apkg")

    return {
        "base": base,
        "data_dir": data_dir,
        "hanzi_dir": hanzi_dir,
        "anki_dir": anki_dir,
    }
