from config.settings import Settings


def test_cors_origin_list_includes_frontend_url_without_duplicates() -> None:
    settings = Settings(
        cors_origins="http://127.0.0.1:5173, https://app.example.com",
        frontend_url="https://app.example.com/",
    )

    assert settings.cors_origin_list() == [
        "http://127.0.0.1:5173",
        "https://app.example.com",
    ]


def test_cors_origin_list_adds_frontend_url() -> None:
    settings = Settings(
        cors_origins="http://127.0.0.1:5173",
        frontend_url="https://finlightai.vercel.app",
    )

    assert settings.cors_origin_list() == [
        "http://127.0.0.1:5173",
        "https://finlightai.vercel.app",
    ]
