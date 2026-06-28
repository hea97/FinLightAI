from __future__ import annotations

import hashlib
import json
import threading
import time
from typing import Any

import httpx

from config.settings import get_settings


class GeminiClient:
    BASE_URL = "https://generativelanguage.googleapis.com/v1beta"
    _cache: dict[str, tuple[float, str]] = {}
    _cache_lock = threading.Lock()

    def __init__(self, api_key: str | None = None, model: str | None = None) -> None:
        settings = get_settings()
        self.api_key = (api_key if api_key is not None else settings.gemini_api_key or "").strip()
        self.model = (model if model is not None else settings.gemini_model).strip()
        self.timeout = settings.external_api_timeout_seconds
        self.cache_seconds = settings.external_api_cache_seconds
        self.last_status = "not_configured" if not self.api_key else "ready"

    @property
    def is_configured(self) -> bool:
        return bool(self.api_key and self.model)

    def generate_text(self, prompt: str, temperature: float = 0.2, max_tokens: int = 512) -> str | None:
        if not self.is_configured:
            self.last_status = "not_configured"
            return None
        cache_key = hashlib.sha256(f"{self.model}|{temperature}|{max_tokens}|{prompt}".encode("utf-8")).hexdigest()
        cached = self._get_cached(cache_key)
        if cached is not None:
            self.last_status = "cached"
            return cached

        url = f"{self.BASE_URL}/models/{self.model}:generateContent"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens,
            },
        }

        try:
            response = httpx.post(url, params={"key": self.api_key}, json=payload, timeout=self.timeout)
            response.raise_for_status()
            text = self._extract_text(response.json())
            if text:
                self._set_cached(cache_key, text)
                self.last_status = "healthy"
            else:
                self.last_status = "empty_response"
            return text
        except httpx.TimeoutException:
            self.last_status = "timeout"
            return None
        except httpx.HTTPStatusError as exc:
            self.last_status = self._status_for_http_error(exc.response.status_code)
            return None
        except (httpx.HTTPError, ValueError, KeyError, TypeError):
            self.last_status = "failed"
            return None

    @staticmethod
    def _status_for_http_error(status_code: int) -> str:
        if status_code == 429:
            return "rate_limited"
        if status_code in {401, 403}:
            return "authentication_failed"
        if status_code == 404:
            return "model_not_found"
        if status_code >= 500:
            return "provider_unavailable"
        return "failed"

    def _get_cached(self, key: str) -> str | None:
        if self.cache_seconds <= 0:
            return None
        with self._cache_lock:
            cached = self._cache.get(key)
            if not cached or time.monotonic() - cached[0] > self.cache_seconds:
                self._cache.pop(key, None)
                return None
            return cached[1]

    def _set_cached(self, key: str, text: str) -> None:
        with self._cache_lock:
            self._cache[key] = (time.monotonic(), text)

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
