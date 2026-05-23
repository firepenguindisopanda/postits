import jwt
from app.utilities.security import encrypt_password, verify_password, create_access_token
from app.config import get_settings


class TestEncryptPassword:
    def test_encrypt_password_returns_hash(self):
        hashed = encrypt_password("MyPassword123!")
        assert hashed != "MyPassword123!"
        assert isinstance(hashed, str)

    def test_encrypt_password_different_each_time(self):
        h1 = encrypt_password("SamePassword")
        h2 = encrypt_password("SamePassword")
        assert h1 != h2

    def test_encrypt_password_empty_string(self):
        hashed = encrypt_password("")
        assert isinstance(hashed, str)
        assert len(hashed) > 0


class TestVerifyPassword:
    def test_verify_correct_password(self):
        hashed = encrypt_password("CorrectPass99!")
        assert verify_password("CorrectPass99!", hashed)

    def test_verify_incorrect_password(self):
        hashed = encrypt_password("RealPass123!")
        assert not verify_password("WrongPass123!", hashed)

    def test_verify_empty_password(self):
        hashed = encrypt_password("SomePass")
        assert not verify_password("", hashed)

    def test_verify_against_different_hash(self):
        h1 = encrypt_password("PassA")
        h2 = encrypt_password("PassB")
        assert not verify_password("PassB", h1)


class TestCreateAccessToken:
    def test_create_token_returns_string(self):
        token = create_access_token(data={"sub": "1", "role": "user"})
        assert isinstance(token, str)
        assert len(token) > 0

    def test_create_token_contains_claims(self):
        token = create_access_token(data={"sub": "42", "role": "admin"})
        payload = jwt.decode(
            token,
            get_settings().secret_key,
            algorithms=[get_settings().jwt_algorithm],
        )
        assert payload["sub"] == "42"
        assert payload["role"] == "admin"

    def test_create_token_has_expiry(self):
        token = create_access_token(data={"sub": "1", "role": "user"})
        payload = jwt.decode(
            token,
            get_settings().secret_key,
            algorithms=[get_settings().jwt_algorithm],
        )
        assert "exp" in payload

    def test_create_token_rejects_none_data(self):
        import pytest
        with pytest.raises((TypeError, AttributeError)):
            create_access_token(data=None)
