from __future__ import annotations

import json
from typing import Any

import httpx

from config.settings import get_settings


class GeminiClient:
    BASE_URL = "https://generativelanguage.googleapis.com/v1beta"

    def __init__(self, api_key: str | None = None, model: str | None = None) -> None:
        settings = get_settings()
        self.api_key = (api_key if api_key is not None else settings.gemini_api_key or "").strip()
        self.model = (model if model is not None else settings.gemini_model).strip()

    @property
    def is_configured(self) -> bool:
        return bool(self.api_key and self.model)

    def generate_text(self, prompt: str, temperature: float = 0.2, max_tokens: int = 512) -> str | None:
        if not self.is_configured:
            return None

        url = f"{self.BASE_URL}/models/{self.model}:generateContent"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens,
            },
        }

        try:
            response = httpx.post(url, params={"key": self.api_key}, json=payload, timeout=20)
            response.raise_for_status()
            return self._extract_text(response.json())
        except (httpx.HTTPError, ValueError, KeyError, TypeError):
            return None

    def generate_briefing(self, articles: list[dict[str, Any]]) -> dict[str, Any] | None:
        if not articles:
            return None

        compact_articles = [
            {
                "title": article.get("title", ""),
                "source": article.get("source") or article.get("domain") or "GDELT",
                "published_at": article.get("published_at", ""),
            }
            for article in articles[:8]
        ]
        prompt = (
            "You are FinLightAI, a market-news briefing assistant. "
            "Summarize these recent AI/semiconductor news items for a dashboard. "
            "Do not give investment advice. Return strict JSON with keys: headline, summary. "
            "headline must be one short sentence. summary must be an array of exactly 3 short bullet strings.\n\n"
            f"Articles:\n{json.dumps(compact_articles, ensure_ascii=False)}"
        )

        text = self.generate_text(prompt, temperature=0.2, max_tokens=512)
        if not text:
            return None
        return self._parse_json_object(text)

    def _extract_text(self, payload: dict[str, Any]) -> str | None:
        candidates = payload.get("candidates") or []
        if not candidates:
            return None
        parts = candidates[0].get("content", {}).get("parts") or []
        text_parts = [part.get("text", "") for part in parts if part.get("text")]
        return "\n".join(text_parts).strip() or None

    def _parse_json_object(self, text: str) -> dict[str, Any] | None:
        cleaned = text.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.strip("`")
            if cleaned.lower().startswith("json"):
                cleaned = cleaned[4:].strip()

        start = cleaned.find("{")
        end = cleaned.rfind("}")
        if start == -1 or end == -1 or end <= start:
            return None

        try:
            parsed = json.loads(cleaned[start : end + 1])
        except json.JSONDecodeError:
            return None

        headline = parsed.get("headline")
        summary = parsed.get("summary")
        if not isinstance(headline, str) or not isinstance(summary, list):
            return None
        return {
            "headline": headline.strip(),
            "summary": [str(item).strip() for item in summary[:3] if str(item).strip()],
        }
