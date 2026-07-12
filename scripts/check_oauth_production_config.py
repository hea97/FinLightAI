from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from typing import Mapping
from urllib.parse import urlparse


CALLBACK_PATH = "/api/auth/google/callback"
MIN_JWT_SECRET_LENGTH = 32

REQUIRED_RENDER_VARS = (
    "GOOGLE_CLIENT_ID",
    "GOOGLE_CLIENT_SECRET",
    "GOOGLE_REDIRECT_URI",
    "FRONTEND_URL",
    "BACKEND_URL",
    "CORS_ORIGINS",
    "JWT_SECRET_KEY",
)


@dataclass(frozen=True)
class Check:
    ok: bool
    message: str


def _value(env: Mapping[str, str], key: str) -> str:
    return (env.get(key) or "").strip()


def _has_placeholder(value: str) -> bool:
    return "<" in value or ">" in value


def _origin(value: str) -> str:
    parsed = urlparse(value)
    if not parsed.scheme or not parsed.netloc:
        return ""
    return f"{parsed.scheme}://{parsed.netloc}".rstrip("/")


def _is_https_origin(value: str) -> bool:
    parsed = urlparse(value)
    return (
        parsed.scheme == "https"
        and bool(parsed.netloc)
        and not parsed.path.rstrip("/")
        and not parsed.params
        and not parsed.query
        and not parsed.fragment
    )


def _cors_origins(value: str) -> list[str]:
    return [origin.strip().rstrip("/") for origin in value.split(",") if origin.strip()]


def validate_config(env: Mapping[str, str]) -> list[Check]:
    checks: list[Check] = []

    for key in REQUIRED_RENDER_VARS:
        checks.append(Check(bool(_value(env, key)), f"{key} is configured" if _value(env, key) else f"{key} is missing"))

    frontend_url = _value(env, "FRONTEND_URL").rstrip("/")
    backend_url = _value(env, "BACKEND_URL").rstrip("/")
    redirect_uri = _value(env, "GOOGLE_REDIRECT_URI")
    cors_value = _value(env, "CORS_ORIGINS")
    jwt_secret = _value(env, "JWT_SECRET_KEY")

    for key in ("FRONTEND_URL", "BACKEND_URL", "GOOGLE_REDIRECT_URI"):
        checks.append(
            Check(
                not _has_placeholder(_value(env, key)),
                f"{key} has no placeholder" if not _has_placeholder(_value(env, key)) else f"{key} still contains a placeholder",
            )
        )

    checks.append(
        Check(
            _is_https_origin(frontend_url),
            "FRONTEND_URL is an HTTPS origin" if _is_https_origin(frontend_url) else "FRONTEND_URL must be an HTTPS origin without a path",
        )
    )
    checks.append(
        Check(
            _is_https_origin(backend_url),
            "BACKEND_URL is an HTTPS origin" if _is_https_origin(backend_url) else "BACKEND_URL must be an HTTPS origin without a path",
        )
    )

    redirect = urlparse(redirect_uri)
    checks.append(
        Check(
            redirect.scheme == "https",
            "GOOGLE_REDIRECT_URI uses HTTPS" if redirect.scheme == "https" else "GOOGLE_REDIRECT_URI must use HTTPS",
        )
    )
    checks.append(
        Check(
            redirect.path == CALLBACK_PATH and not redirect.params and not redirect.query and not redirect.fragment,
            "GOOGLE_REDIRECT_URI callback path is valid"
            if redirect.path == CALLBACK_PATH and not redirect.params and not redirect.query and not redirect.fragment
            else f"GOOGLE_REDIRECT_URI callback path must be {CALLBACK_PATH}",
        )
    )
    checks.append(
        Check(
            bool(backend_url) and _origin(redirect_uri) == backend_url,
            "GOOGLE_REDIRECT_URI origin matches BACKEND_URL"
            if bool(backend_url) and _origin(redirect_uri) == backend_url
            else "GOOGLE_REDIRECT_URI origin must match BACKEND_URL",
        )
    )

    cors_origins = _cors_origins(cors_value)
    checks.append(
        Check(
            "*" not in cors_origins,
            "CORS_ORIGINS does not include wildcard" if "*" not in cors_origins else "CORS_ORIGINS must not include wildcard",
        )
    )
    checks.append(
        Check(
            frontend_url in cors_origins,
            "CORS_ORIGINS includes FRONTEND_URL" if frontend_url in cors_origins else "CORS_ORIGINS does not include FRONTEND_URL",
        )
    )
    checks.append(
        Check(
            all(not _has_placeholder(origin) for origin in cors_origins),
            "CORS_ORIGINS has no placeholder"
            if all(not _has_placeholder(origin) for origin in cors_origins)
            else "CORS_ORIGINS still contains a placeholder",
        )
    )
    checks.append(
        Check(
            len(jwt_secret) >= MIN_JWT_SECRET_LENGTH,
            "JWT_SECRET_KEY length is acceptable"
            if len(jwt_secret) >= MIN_JWT_SECRET_LENGTH
            else f"JWT_SECRET_KEY must be at least {MIN_JWT_SECRET_LENGTH} characters",
        )
    )

    return checks


def main() -> int:
    checks = validate_config(os.environ)
    for check in checks:
        status = "PASS" if check.ok else "FAIL"
        print(f"[{status}] {check.message}")
    return 0 if all(check.ok for check in checks) else 1


if __name__ == "__main__":
    sys.exit(main())
