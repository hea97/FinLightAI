from types import SimpleNamespace

from fastapi.testclient import TestClient

from src.dashboard import auth as auth_helpers
from src.dashboard.app import app
from src.dashboard.models import User, UserPreference
from src.dashboard.routes import api as api_routes


def _settings(**overrides):
    values = {
        "app_env": "local",
        "frontend_url": "https://frontend.example.com",
        "google_client_id": "google-client-id",
        "google_client_secret": "google-client-secret",
        "google_redirect_uri": "https://backend.example.com/api/auth/google/callback",
        "jwt_secret_key": "unit-test-secret",
        "jwt_expire_minutes": 1440,
        "auth_cookie_name": "finlight_session",
        "auth_cookie_domain": None,
        "auth_cookie_samesite": None,
        "auth_cookie_secure": None,
        "oauth_state_cookie_name": "finlight_oauth_state",
        "external_api_timeout_seconds": 10,
        "news_api_key": None,
        "guardian_api_key": None,
        "finnhub_api_key": None,
        "alpha_vantage_api_key": None,
        "gemini_api_key": None,
        "openai_api_key": None,
        "opendart_api_key": None,
        "kis_app_key": None,
        "kis_app_secret": None,
        "kakao_rest_api_key": None,
        "min_source_score": 0.8,
    }
    values.update(overrides)
    settings = SimpleNamespace(**values)
    settings.is_development = lambda: settings.app_env in {"local", "development", "dev", "test"}
    settings.session_cookie_secure = lambda: (
        True
        if not settings.is_development()
        else bool(settings.auth_cookie_secure)
    )
    settings.session_cookie_samesite = lambda: (
        "none"
        if not settings.is_development()
        else (settings.auth_cookie_samesite or "lax")
    )
    return settings


def _begin_google_login(client: TestClient) -> str:
    response = client.get("/api/auth/google/login", follow_redirects=False)
    assert response.status_code == 302
    return client.cookies["finlight_oauth_state"]


def test_google_login_redirects_to_google_authorization_url(monkeypatch):
    monkeypatch.setattr(api_routes, "get_settings", lambda: _settings())

    response = TestClient(app).get("/api/auth/google/login", follow_redirects=False)

    assert response.status_code == 302
    location = response.headers["location"]
    assert location.startswith(auth_helpers.GOOGLE_AUTH_URL)
    assert "client_id=google-client-id" in location
    assert "scope=openid+email+profile" in location
    assert "finlight_oauth_state=" in response.headers["set-cookie"]


def test_google_callback_creates_user_sets_cookie_and_me_returns_user(monkeypatch, isolated_dashboard_database):
    monkeypatch.setattr(api_routes, "get_settings", lambda: _settings())
    monkeypatch.setattr(
        api_routes,
        "exchange_google_code",
        lambda **kwargs: {"access_token": "mock-access-token"},
    )
    monkeypatch.setattr(
        api_routes,
        "fetch_google_userinfo",
        lambda access_token, timeout=10: {
            "sub": "google-sub-123",
            "email": "user@example.com",
            "name": "Google User",
            "picture": "https://example.com/avatar.png",
        },
    )
    client = TestClient(app, base_url="https://backend.example.com")
    state = _begin_google_login(client)

    callback = client.get(
        f"/api/auth/google/callback?code=mock-code&state={state}",
        follow_redirects=False,
    )

    assert callback.status_code == 302
    assert callback.headers["location"] == "https://frontend.example.com/?auth=google_connected"
    assert "finlight_session=" in callback.headers["set-cookie"]

    current = client.get("/api/auth/me")
    assert current.status_code == 200
    payload = current.json()
    assert payload["authenticated"] is True
    assert payload["user"]["provider"] == "google"
    assert payload["user"]["email"] == "user@example.com"
    assert payload["user"]["profileImageUrl"] == "https://example.com/avatar.png"

    with isolated_dashboard_database() as db:
        user = db.query(User).filter_by(provider="google", provider_user_id="google-sub-123").one()
        assert user.email == "user@example.com"
        assert db.get(UserPreference, user.id) is not None


def test_google_callback_reuses_existing_user(monkeypatch, isolated_dashboard_database):
    monkeypatch.setattr(api_routes, "get_settings", lambda: _settings())
    monkeypatch.setattr(api_routes, "exchange_google_code", lambda **kwargs: {"access_token": "first-token"})
    monkeypatch.setattr(
        api_routes,
        "fetch_google_userinfo",
        lambda access_token, timeout=10: {
            "sub": "same-google-sub",
            "email": "updated@example.com",
            "name": "Updated Name",
            "picture": None,
        },
    )
    client = TestClient(app)
    first_state = _begin_google_login(client)

    first = client.get(
        f"/api/auth/google/callback?code=one&state={first_state}",
        follow_redirects=False,
    )
    second_state = _begin_google_login(client)
    second = client.get(
        f"/api/auth/google/callback?code=two&state={second_state}",
        follow_redirects=False,
    )

    assert first.status_code == 302
    assert second.status_code == 302
    with isolated_dashboard_database() as db:
        assert db.query(User).filter_by(provider="google", provider_user_id="same-google-sub").count() == 1


def test_logout_clears_session_cookie(monkeypatch):
    monkeypatch.setattr(api_routes, "get_settings", lambda: _settings())

    response = TestClient(app).post("/api/auth/logout")

    assert response.status_code == 204
    assert "finlight_session=" in response.headers["set-cookie"]


def test_production_logout_uses_matching_cookie_security(monkeypatch):
    monkeypatch.setattr(api_routes, "get_settings", lambda: _settings(app_env="production"))

    response = TestClient(app, base_url="https://backend.example.com").post("/api/auth/logout")

    cookie = response.headers["set-cookie"]
    assert "finlight_session=" in cookie
    assert "HttpOnly" in cookie
    assert "Path=/" in cookie
    assert "Secure" in cookie
    assert "SameSite=none" in cookie


def test_auth_me_is_anonymous_without_session(monkeypatch):
    monkeypatch.setattr(api_routes, "get_settings", lambda: _settings())

    response = TestClient(app).get("/api/auth/me")

    assert response.status_code == 200
    assert response.json() == {"authenticated": False, "user": None}


def test_google_callback_rejects_invalid_oauth_state(monkeypatch):
    monkeypatch.setattr(api_routes, "get_settings", lambda: _settings())
    client = TestClient(app)
    _begin_google_login(client)

    response = client.get(
        "/api/auth/google/callback?code=mock-code&state=wrong-state",
        follow_redirects=False,
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid OAuth state"


def test_production_session_cookie_is_secure_and_cross_site(monkeypatch, isolated_dashboard_database):
    monkeypatch.setattr(api_routes, "get_settings", lambda: _settings(app_env="production"))
    monkeypatch.setattr(api_routes, "exchange_google_code", lambda **kwargs: {"access_token": "token"})
    monkeypatch.setattr(
        api_routes,
        "fetch_google_userinfo",
        lambda access_token, timeout=10: {
            "sub": "production-google-user",
            "email": "production@example.com",
            "name": "Production User",
        },
    )
    client = TestClient(app, base_url="https://backend.example.com")
    state = _begin_google_login(client)

    response = client.get(
        f"/api/auth/google/callback?code=mock-code&state={state}",
        follow_redirects=False,
    )

    session_cookie = next(
        header
        for header in response.headers.get_list("set-cookie")
        if header.startswith("finlight_session=")
    )
    assert "HttpOnly" in session_cookie
    assert "Secure" in session_cookie
    assert "SameSite=none" in session_cookie


def test_x_user_id_fallback_is_disabled_in_production(monkeypatch):
    monkeypatch.setattr(api_routes, "get_settings", lambda: _settings(app_env="production"))

    response = TestClient(app).get("/api/portfolio", headers={"X-User-ID": "demo-user"})

    assert response.status_code == 401


def test_onboarding_preferences_are_scoped_to_authenticated_user(monkeypatch):
    monkeypatch.setattr(api_routes, "get_settings", lambda: _settings())
    token = auth_helpers.create_session_token(
        "google-test-user",
        secret="unit-test-secret",
        expire_minutes=1440,
    )
    client = TestClient(app, cookies={"finlight_session": token})
    # Create the local test user through development fallback first.
    client.get("/api/mypage", headers={"X-User-ID": "google-test-user"})

    saved = client.put(
        "/api/onboarding/preferences",
        json={
            "interestedMarkets": ["US", "KR", "US"],
            "interestedIndustries": ["AI", "Semiconductor", "AI"],
            "alertEnabled": False,
            "notificationChannels": ["dashboard", "email"],
        },
    )

    assert saved.status_code == 200
    payload = saved.json()
    assert payload["userId"] == "google-test-user"
    assert payload["interestedMarkets"] == ["US", "KR"]
    assert payload["interestedIndustries"] == ["AI", "Semiconductor"]
    assert payload["alertEnabled"] is False
    assert client.get("/api/mypage").json()["interests"] == ["AI", "Semiconductor"]


def test_settings_updates_use_authenticated_user_context(monkeypatch):
    monkeypatch.setattr(api_routes, "get_settings", lambda: _settings())
    token = auth_helpers.create_session_token(
        "google-settings-user",
        secret="unit-test-secret",
        expire_minutes=1440,
    )
    client = TestClient(app, cookies={"finlight_session": token})
    client.get("/api/mypage", headers={"X-User-ID": "google-settings-user"})

    payload = client.get("/api/settings").json()
    payload["notifications"][0]["enabled"] = False
    writable = {
        key: payload[key]
        for key in ["dataCollection", "newsGuard", "notifications", "display", "misc"]
    }

    assert client.put("/api/settings", json=writable).status_code == 200
    assert client.get("/api/settings").json()["notifications"][0]["enabled"] is False
