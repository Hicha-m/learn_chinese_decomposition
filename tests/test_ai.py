from modules import ai


class FakeModels:
    def generate_content(self, model, contents):
        class Resp:
            text = "ok"
        return Resp()


class FakeClient:
    def __init__(self, api_key=None):
        self.models = FakeModels()


def test_geminiAI_mocked_client(monkeypatch):
    monkeypatch.setattr(ai.genai, "Client", FakeClient)

    assert ai.geminiAI("prompt") == "ok"


def test_openrouterAI_handles_exception(monkeypatch):
    class Boom:
        def __init__(self, *args, **kwargs):
            raise RuntimeError("fail")

    monkeypatch.setattr(ai, "OpenAI", Boom)

    assert ai.openrouterAI(model="x", prompt="y") == ""


def test_openrouterAI_success(monkeypatch):
    class FakeOpenAI:
        def __init__(self, *args, **kwargs):
            class Chat:
                class Completions:
                    def create(self, *args, **kwargs):
                        message = type("Msg", (), {"content": "ok"})()
                        choice = type("Choice", (), {"message": message})()
                        return type("Resp", (), {"choices": [choice]})()

                completions = Completions()

            self.chat = Chat()

    monkeypatch.setattr(ai, "OpenAI", FakeOpenAI)

    assert ai.openrouterAI(model="x", prompt="y") == "ok"


def test_openrouterAIRes_handles_exception(monkeypatch):
    class Boom:
        def __init__(self, *args, **kwargs):
            raise RuntimeError("fail")

    monkeypatch.setattr(ai, "OpenAI", Boom)

    assert ai.openrouterAIRes(model="x", prompt="y", question="z") == ""
