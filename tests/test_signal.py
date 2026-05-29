from src.signal.generator import SignalGenerator


def test_red_signal_requires_negative_sentiment_volume_and_volatility() -> None:
    signal = SignalGenerator().generate(
        0.9,
        {"return_1d": -0.04, "volume_ratio": 2.3, "volatility_5d": 0.07, "sentiment_score": -0.6},
        [],
    )
    assert signal == "RED"


def test_fake_news_flags_force_green() -> None:
    signal = SignalGenerator().generate(
        0.9,
        {"return_1d": -0.04, "volume_ratio": 2.3, "volatility_5d": 0.07, "sentiment_score": -0.6},
        ["untrusted_source"],
    )
    assert signal == "GREEN"
