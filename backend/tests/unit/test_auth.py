from app.services.auth_service import (
    create_access_token,
    create_magic_link_token,
    create_refresh_token,
    create_token_pair,
    decode_token,
    verify_magic_link_token,
)
from app.core.exceptions import AuthenticationError
import pytest


def test_create_and_decode_access_token():
    user_id = "test-user-123"
    token = create_access_token(user_id)
    payload = decode_token(token)
    assert payload["sub"] == user_id
    assert payload["type"] == "access"


def test_create_and_decode_refresh_token():
    user_id = "test-user-123"
    token = create_refresh_token(user_id)
    payload = decode_token(token)
    assert payload["sub"] == user_id
    assert payload["type"] == "refresh"


def test_token_pair():
    pair = create_token_pair("test-user-123")
    assert "access_token" in pair
    assert "refresh_token" in pair
    assert pair["token_type"] == "bearer"


def test_decode_invalid_token():
    with pytest.raises(AuthenticationError):
        decode_token("invalid-token-string")


def test_magic_link_create_and_verify():
    email = "test@example.com"
    token = create_magic_link_token(email)
    result = verify_magic_link_token(token)
    assert result == email


def test_magic_link_invalid_token():
    with pytest.raises(AuthenticationError):
        verify_magic_link_token("bad-token")
