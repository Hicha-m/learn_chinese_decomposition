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
