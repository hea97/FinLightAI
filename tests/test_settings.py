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
        cors_origins="http://127.0.0.1:5173/",
        frontend_url="https://finlightai.vercel.app",
    )

    assert settings.cors_origin_list() == [
        "http://127.0.0.1:5173",
        "https://finlightai.vercel.app",
    ]


def test_production_cookie_defaults_support_cross_site_https() -> None:
    settings = Settings(app_env="production")

    assert settings.session_cookie_secure() is True
    assert settings.session_cookie_samesite() == "none"


def test_local_cookie_defaults_remain_http_compatible() -> None:
    settings = Settings(app_env="local")

    assert settings.session_cookie_secure() is False
    assert settings.session_cookie_samesite() == "lax"


def test_production_cookie_security_cannot_be_disabled_by_environment() -> None:
    settings = Settings(
        app_env="production",
        auth_cookie_secure=False,
        auth_cookie_samesite="lax",
    )

    assert settings.session_cookie_secure() is True
    assert settings.session_cookie_samesite() == "none"
