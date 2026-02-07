from modules import pinyin, data


def test_split_pinyin_numeric_and_mark(patch_paths):
    initial, final, tone = pinyin.split_pinyin("shi4")
    assert (initial, final, tone) == ("sh", "i", "4")

    initial, final, tone = pinyin.split_pinyin("sh\u00ec")
    assert (initial, final, tone) == ("sh", "i", "4")


def test_split_pinyin_edge_cases(patch_paths):
    assert pinyin.split_pinyin("") == ("", "", "")
    assert pinyin.split_pinyin("invalid") == ("", "invalid", "5")
    assert pinyin.split_pinyin("shi") == ("sh", "i", "5")


def test_get_pinyin_rules_aliasing(patch_paths):
    rules = {
        "initials": {"yi": "actor"},
        "finals": {"en": "scene", "eng": "scene2"},
        "tones": {"1": "tone1"},
    }
    data.save_pinyin_rules(rules)

    assert pinyin.get_pinyin_rules("initials", "y") == "actor"
    assert pinyin.get_pinyin_rules("finals", "n") == "scene"
    assert pinyin.get_pinyin_rules("finals", "ng") == "scene2"
    assert pinyin.get_pinyin_rules("initials", "yi") == "actor"
