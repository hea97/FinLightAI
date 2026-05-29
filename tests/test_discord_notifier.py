import httpx

from src.notifier.discord_bot import DiscordNotifier


def test_discord_payload_contains_alert_fields() -> None:
    notifier = DiscordNotifier(webhook_url=None)
    payload = notifier.build_signal_payload(
        "RED",
        "005930.KS",
        {"headline": "Policy risk", "return_1d": -0.032, "volume_ratio": 3.5, "reliability_score": 0.87},
    )
    embed = payload["embeds"][0]
    assert "RED signal" in embed["title"]
    assert embed["color"] == DiscordNotifier.COLORS["RED"]
    assert any(field["name"] == "Reliability" for field in embed["fields"])


def test_discord_alert_posts_for_red_signal() -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(204)

    client = httpx.Client(transport=httpx.MockTransport(handler))
    notifier = DiscordNotifier(webhook_url="https://discord.test/webhook", client=client)
    sent = notifier.send_signal_alert("RED", "NVDA", {"headline": "AI chip policy", "return_1d": -0.01})
    assert sent is True
    assert len(requests) == 1


def test_discord_alert_skips_green_signal() -> None:
    notifier = DiscordNotifier(webhook_url="https://discord.test/webhook")
    assert notifier.send_signal_alert("GREEN", "NVDA", {}) is False
