from __future__ import annotations

import base64
import hashlib
import hmac
import json
from datetime import datetime, timedelta, timezone
from typing import Any
from urllib.parse import urlencode

import httpx

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://openidconnect.googleapis.com/v1/userinfo"
GOOGLE_SCOPES = ("openid", "email", "profile")


class AuthConfigurationError(RuntimeError):
    pass


class OAuthExchangeError(RuntimeError):
    pass


def build_google_authorization_url(
    *,
    client_id: str | None,
    redirect_uri: str | None,
    state: str,
) -> str:
    if not client_id or not redirect_uri:
        raise AuthConfigurationError("Google OAuth is not configured")
    query = urlencode(
        {
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": " ".join(GOOGLE_SCOPES),
            "state": state,
            "access_type": "offline",
            "prompt": "select_account",
        }
    )
    return f"{GOOGLE_AUTH_URL}?{query}"


def exchange_google_code(
    *,
    code: str,
    client_id: str | None,
    client_secret: str | None,
    redirect_uri: str | None,
    timeout: float = 10,
) -> dict[str, Any]:
    if not client_id or not client_secret or not redirect_uri:
        raise AuthConfigurationError("Google OAuth is not configured")
    response = httpx.post(
        GOOGLE_TOKEN_URL,
        data={
            "code": code,
            "client_id": client_id,
            "client_secret": client_secret,
            "redirect_uri": redirect_uri,
            "grant_type": "authorization_code",
        },
        timeout=timeout,
    )
    if response.status_code >= 400:
        raise OAuthExchangeError("Google token exchange failed")
    return response.json()


def fetch_google_userinfo(access_token: str, *, timeout: float = 10) -> dict[str, Any]:
    response = httpx.get(
        GOOGLE_USERINFO_URL,
        headers={"Authorization": f"Bearer {access_token}"},
        timeout=timeout,
    )
    if response.status_code >= 400:
        raise OAuthExchangeError("Google userinfo request failed")
    payload = response.json()
    if not payload.get("sub") or not payload.get("email"):
        raise OAuthExchangeError("Google userinfo response is missing identity fields")
    return payload


def create_session_token(user_id: str, *, secret: str | None, expire_minutes: int) -> str:
    if not secret:
        raise AuthConfigurationError("JWT_SECRET_KEY is not configured")
    now = datetime.now(timezone.utc)
    payload = {
        "sub": user_id,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=expire_minutes)).timestamp()),
    }
    header = {"alg": "HS256", "typ": "JWT"}
    signing_input = f"{_b64_json(header)}.{_b64_json(payload)}"
    signature = _b64_bytes(hmac.new(secret.encode("utf-8"), signing_input.encode("utf-8"), hashlib.sha256).digest())
    return f"{signing_input}.{signature}"


def verify_session_token(token: str, *, secret: str | None) -> str | None:
    if not secret:
        return None
    try:
        header_b64, payload_b64, signature = token.split(".", 2)
        signing_input = f"{header_b64}.{payload_b64}"
        expected = _b64_bytes(hmac.new(secret.encode("utf-8"), signing_input.encode("utf-8"), hashlib.sha256).digest())
        if not hmac.compare_digest(signature, expected):
            return None
        payload = json.loads(_b64_decode(payload_b64))
        if int(payload.get("exp", 0)) < int(datetime.now(timezone.utc).timestamp()):
            return None
        subject = payload.get("sub")
        return str(subject) if subject else None
    except (ValueError, json.JSONDecodeError, TypeError):
        return None


def _b64_json(payload: dict[str, Any]) -> str:
    return _b64_bytes(json.dumps(payload, separators=(",", ":")).encode("utf-8"))


def _b64_bytes(payload: bytes) -> str:
    return base64.urlsafe_b64encode(payload).rstrip(b"=").decode("ascii")


def _b64_decode(payload: str) -> str:
    padded = payload + "=" * (-len(payload) % 4)
    return base64.urlsafe_b64decode(padded.encode("ascii")).decode("utf-8")
