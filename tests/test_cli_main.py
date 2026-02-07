import builtins

import modules.ai as ai
import modules.anki as anki
import modules.data as data
import modules.learning as learning
import modules.main as main


def _feed_inputs(monkeypatch, values):
    inputs = iter(values)
    monkeypatch.setattr(builtins, "input", lambda _prompt="": next(inputs))


def _mock_learn_flow(monkeypatch, *, fail_save=False):
    monkeypatch.setattr(data, "load_learned_chars", lambda: set())
    monkeypatch.setattr(
        learning,
        "learn_character",
        lambda target, builder, learned: (target, "r1 + r2", "ok"),
    )
    monkeypatch.setattr(
        learning,
        "build_dictionary_result",
        lambda char: {
            "character": char,
            "pinyin": ["zhi3"],
            "definition": [{"definition": "stop"}],
            "search": [],
        },
    )
    monkeypatch.setattr(learning, "select_pinyin", lambda option: "zhi3")
    monkeypatch.setattr(ai, "build_prompt", lambda char: "prompt")
    monkeypatch.setattr(ai, "openrouterAIRes", lambda model, prompt: "explain")
    monkeypatch.setattr(data, "save_hanzi", lambda char, text, name: None)
    monkeypatch.setattr(data, "load_word_to_bubbles", lambda: {})
    monkeypatch.setattr(data, "load_bubbles", lambda: [])
    monkeypatch.setattr(learning, "get_exemple", lambda *args, **kwargs: "发卫")
    monkeypatch.setattr(
        learning,
        "collect_pinyin_mnemonics",
        lambda selected_pinyin, easy_note=False: ("label", "", "", "3", {}),
    )
    monkeypatch.setattr(
        learning,
        "characteristics_hanzi",
        lambda *args, **kwargs: [
            "止",
            "止",
            "zhi3",
            "stop",
            "",
            "发卫",
            "label",
            "r1 + r2",
            "",
            "",
            "bedroom",
            "z",
            "hi",
            "3",
            [],
        ],
    )
    monkeypatch.setattr(anki, "get_chinese_model", lambda: object())
    monkeypatch.setattr(
        anki,
        "note_anki_chinese",
        lambda model, args, easy_note=False: (object(), easy_note),
    )

    if fail_save:
        def raise_save(*_args, **_kwargs):
            raise RuntimeError("fail")

        monkeypatch.setattr(anki, "save_note_anki", raise_save)
        return None, None

    save_called = {"value": False}

    def fake_save(note, easy_note=False):
        save_called["value"] = True

    monkeypatch.setattr(anki, "save_note_anki", fake_save)

    marked = {"char": None}

    def fake_mark(char, learned):
        marked["char"] = char

    monkeypatch.setattr(learning, "mark_as_learned", fake_mark)

    return save_called, marked


def test_menu_show_progress(monkeypatch, isolate_paths, capsys):
    monkeypatch.setattr(data, "load_learned_chars", lambda: {"一", "二"})
    monkeypatch.setattr(
        data,
        "load_learned_chars_characteristic",
        lambda: {
            "一": {"pinyin": "yi1", "english": "one"},
            "二": {"pinyin": "er4", "english": "two"},
        },
    )

    _feed_inputs(monkeypatch, ["2"])
    main.main()

    out = capsys.readouterr().out
    assert "Learning Progress" in out
    assert "Characters learned: 2" in out
    assert "Characters with details: 2" in out


def test_menu_export_session(monkeypatch, isolate_paths, capsys):
    called = {"value": False}

    def fake_export():
        called["value"] = True

    monkeypatch.setattr(anki, "export_anki", fake_export)

    _feed_inputs(monkeypatch, ["4"])
    main.main()

    out = capsys.readouterr().out
    assert "Exporting current session to Anki" in out
    assert called["value"] is True


def test_menu_export_all(monkeypatch, isolate_paths, capsys):
    called = {"value": False}

    def fake_export():
        called["value"] = True

    monkeypatch.setattr(anki, "export_chars_learn_to_anki", fake_export)

    _feed_inputs(monkeypatch, ["3"])
    main.main()

    out = capsys.readouterr().out
    assert "Exporting to Anki" in out
    assert called["value"] is True


def test_menu_learn_flow(monkeypatch, isolate_paths, capsys):
    save_called, marked = _mock_learn_flow(monkeypatch)

    _feed_inputs(monkeypatch, ["1", "止", "n"])
    main.main()

    out = capsys.readouterr().out
    assert "Learning character" in out
    assert save_called["value"] is True
    assert marked["char"] == "止"


def test_menu_exit(monkeypatch, isolate_paths, capsys):
    _feed_inputs(monkeypatch, ["0"])
    main.main()

    out = capsys.readouterr().out
    assert "Goodbye" in out


def test_menu_demo(monkeypatch, isolate_paths, capsys):
    called = {"char": None}

    def fake_learn(character):
        called["char"] = character

    monkeypatch.setattr(main, "learn_new_character", fake_learn)
    _feed_inputs(monkeypatch, ["5"])
    main.main()

    out = capsys.readouterr().out
    assert "Demo" in out
    assert called["char"] == "是"


def test_menu_invalid_input(monkeypatch, isolate_paths, capsys):
    _feed_inputs(monkeypatch, ["x"])
    main.main()

    out = capsys.readouterr().out
    assert "Invalid option" in out


def test_menu_learn_flow_anki_failure(monkeypatch, isolate_paths, capsys):
    _mock_learn_flow(monkeypatch, fail_save=True)

    _feed_inputs(monkeypatch, ["1", "止", "n"])
    main.main()

    out = capsys.readouterr().out
    assert "Card creation failed" in out
