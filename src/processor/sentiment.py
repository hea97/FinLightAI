from __future__ import annotations


class SentimentAnalyzer:
    POSITIVE_WORDS = {"gain", "growth", "beat", "strong", "surge", "benefit", "positive", "호재", "상승"}
    NEGATIVE_WORDS = {"loss", "risk", "weak", "drop", "ban", "restriction", "negative", "악재", "하락", "규제"}

    def analyze(self, text: str, lang: str = "en") -> dict[str, float | str]:
        lowered = text.lower()
        positive = sum(1 for word in self.POSITIVE_WORDS if word in lowered)
        negative = sum(1 for word in self.NEGATIVE_WORDS if word in lowered)
        total = max(positive + negative, 1)
        score = (positive - negative) / total
        label = "positive" if score > 0.2 else "negative" if score < -0.2 else "neutral"
        confidence = min(1.0, abs(score) + 0.5)
        return {"score": round(score, 4), "label": label, "confidence": round(confidence, 4)}

    def batch_analyze(self, texts: list[str]) -> list[dict[str, float | str]]:
        return [self.analyze(text) for text in texts]
