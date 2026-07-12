from scripts.check_oauth_production_config import main, validate_config


def valid_env() -> dict[str, str]:
    return {
        "GOOGLE_CLIENT_ID": "configured-client-id",
        "GOOGLE_CLIENT_SECRET": "configured-client-secret",
        "GOOGLE_REDIRECT_URI": "https://api.example.com/api/auth/google/callback",
        "FRONTEND_URL": "https://app.example.com",
        "BACKEND_URL": "https://api.example.com",
        "CORS_ORIGINS": "https://app.example.com",
        "JWT_SECRET_KEY": "x" * 32,
    }


def assert_fails(env: dict[str, str], expected: str) -> None:
    checks = validate_config(env)
    assert any((not check.ok) and expected in check.message for check in checks)


def test_valid_production_config_passes() -> None:
    assert all(check.ok for check in validate_config(valid_env()))


def test_missing_google_client_id_fails() -> None:
    env = valid_env()
    env.pop("GOOGLE_CLIENT_ID")

    assert_fails(env, "GOOGLE_CLIENT_ID is missing")


def test_missing_google_client_secret_fails() -> None:
    env = valid_env()
    env.pop("GOOGLE_CLIENT_SECRET")

    assert_fails(env, "GOOGLE_CLIENT_SECRET is missing")


def test_http_url_fails() -> None:
    env = valid_env()
    env["FRONTEND_URL"] = "http://app.example.com"
    env["CORS_ORIGINS"] = "http://app.example.com"

    assert_fails(env, "FRONTEND_URL must be an HTTPS origin")


def test_callback_path_mismatch_fails() -> None:
    env = valid_env()
    env["GOOGLE_REDIRECT_URI"] = "https://api.example.com/auth/google/callback"

    assert_fails(env, "GOOGLE_REDIRECT_URI callback path must be /api/auth/google/callback")


def test_callback_origin_mismatch_fails() -> None:
    env = valid_env()
    env["GOOGLE_REDIRECT_URI"] = "https://other-api.example.com/api/auth/google/callback"

    assert_fails(env, "GOOGLE_REDIRECT_URI origin must match BACKEND_URL")


def test_cors_wildcard_fails() -> None:
    env = valid_env()
    env["CORS_ORIGINS"] = "https://app.example.com,*"

    assert_fails(env, "CORS_ORIGINS must not include wildcard")


def test_cors_missing_frontend_origin_fails() -> None:
    env = valid_env()
    env["CORS_ORIGINS"] = "https://other-app.example.com"

    assert_fails(env, "CORS_ORIGINS does not include FRONTEND_URL")


def test_placeholder_url_fails() -> None:
    env = valid_env()
    env["BACKEND_URL"] = "https://<render-production-domain>"
    env["GOOGLE_REDIRECT_URI"] = "https://<render-production-domain>/api/auth/google/callback"

    assert_fails(env, "BACKEND_URL still contains a placeholder")


def test_short_jwt_secret_fails() -> None:
    env = valid_env()
    env["JWT_SECRET_KEY"] = "short"

    assert_fails(env, "JWT_SECRET_KEY must be at least 32 characters")


def test_output_does_not_expose_secret_values(monkeypatch, capsys) -> None:
    secret_value = "super-sensitive-google-secret"
    jwt_value = "super-sensitive-jwt-secret-value"
    env = valid_env()
    env["GOOGLE_CLIENT_SECRET"] = secret_value
    env["JWT_SECRET_KEY"] = jwt_value
    monkeypatch.setattr("os.environ", env)

    assert main() == 0
    output = capsys.readouterr().out
    assert secret_value not in output
    assert jwt_value not in output


def test_main_returns_one_when_checks_fail(monkeypatch, capsys) -> None:
    monkeypatch.setattr("os.environ", {})

    assert main() == 1
    assert "[FAIL] GOOGLE_CLIENT_ID is missing" in capsys.readouterr().out
