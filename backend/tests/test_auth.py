from __future__ import annotations

from app.core.security import create_access_token, decode_access_token, get_password_hash, verify_password


def test_password_hashing():
    hashed = get_password_hash("testpassword123")
    assert verify_password("testpassword123", hashed)
    assert not verify_password("wrongpassword", hashed)


def test_jwt_token():
    token = create_access_token({"sub": "1"})
    payload = decode_access_token(token)
    assert payload is not None
    assert payload["sub"] == "1"
