from src.processor.gemini_client import GeminiClient


def test_gemini_client_extracts_text_from_generate_content_response():
    client = GeminiClient(api_key="", model="gemini-test")

    text = client._extract_text(
        {
            "candidates": [
                {
                    "content": {
                        "parts": [
                            {"text": "hello"},
                            {"text": "world"},
                        ]
                    }
                }
            ]
        }
    )

    assert text == "hello\nworld"


def test_gemini_client_parses_json_wrapped_in_markdown():
    client = GeminiClient(api_key="", model="gemini-test")

    parsed = client._parse_json_object('```json\n{"headline":"Ready","summary":["A","B","C"]}\n```')

    assert parsed == {"headline": "Ready", "summary": ["A", "B", "C"]}


def test_gemini_client_caches_successful_responses(monkeypatch):
    GeminiClient._cache.clear()
    calls = 0

    class Response:
        def raise_for_status(self):
            return None

        def json(self):
            return {"candidates": [{"content": {"parts": [{"text": "cached result"}]}}]}

    def fake_post(*args, **kwargs):
        nonlocal calls
        calls += 1
        return Response()

    monkeypatch.setattr("src.processor.gemini_client.httpx.post", fake_post)
    client = GeminiClient(api_key="test-key", model="gemini-test")

    assert client.generate_text("same prompt") == "cached result"
    assert client.generate_text("same prompt") == "cached result"
    assert calls == 1
    assert client.last_status == "cached"
