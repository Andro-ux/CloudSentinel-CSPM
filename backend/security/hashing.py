import os
import hashlib
import secrets
from typing import Optional


def hash_password(password: str) -> str:
    salt = os.urandom(16)
    db_hash = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt,
        100000,
    )
    return f"{salt.hex()}${db_hash.hex()}"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        salt_hex, hash_hex = hashed_password.split("$")
        salt = bytes.fromhex(salt_hex)
        db_hash = bytes.fromhex(hash_hex)
        new_hash = hashlib.pbkdf2_hmac(
            'sha256',
            plain_password.encode('utf-8'),
            salt,
            100000,
        )
        return new_hash == db_hash
    except Exception:
        return False


def hash_api_key_secret(secret: str) -> str:
    return hashlib.sha256(secret.encode('utf-8')).hexdigest()


def generate_api_key_secret() -> str:
    return secrets.token_urlsafe(32)


def validate_password_strength(password: str, min_length: int = 12) -> None:
    if len(password) < min_length:
        raise ValueError(f"Password must be at least {min_length} characters long")
