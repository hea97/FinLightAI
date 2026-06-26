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
