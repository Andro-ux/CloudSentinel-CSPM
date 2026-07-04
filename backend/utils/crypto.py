import os
from functools import lru_cache
from cryptography.fernet import Fernet, InvalidToken

# Setting keys that must ALWAYS be encrypted at rest, regardless of what the
# is_encrypted flag in the request says. Never trust the client to decide this —
# a buggy or malicious client request shouldn't be able to store a secret in plaintext.
SENSITIVE_SETTING_KEYS = {
    "SLACK_WEBHOOK_URL",
    "JIRA_API_TOKEN",
    "JIRA_USER",
    "OPENAI_API_KEY",
}


class EncryptionConfigError(Exception):
    """Raised when SECRET_ENCRYPTION_KEY is missing or invalid."""


@lru_cache(maxsize=1)
def _get_fernet() -> Fernet:
    key = os.getenv("SECRET_ENCRYPTION_KEY")
    if not key:
        raise EncryptionConfigError(
            "SECRET_ENCRYPTION_KEY is not set. Generate one with "
            "`python -c \"from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())\"` "
            "and set it as an environment variable. This is required before any encrypted "
            "setting (Slack webhook, Jira token, OpenAI key, etc.) can be stored or read."
        )
    try:
        return Fernet(key.encode() if isinstance(key, str) else key)
    except (ValueError, TypeError) as e:
        raise EncryptionConfigError(f"SECRET_ENCRYPTION_KEY is not a valid Fernet key: {e}") from e


def encrypt_value(plaintext: str) -> str:
    """Encrypts a string for storage. Returns a base64 token safe to store as text."""
    if plaintext is None:
        return None
    return _get_fernet().encrypt(plaintext.encode("utf-8")).decode("utf-8")


def decrypt_value(token: str) -> str:
    """Decrypts a value previously produced by encrypt_value. Raises EncryptionConfigError
    if the key is missing/wrong, or ValueError if the token is corrupt/not encrypted with
    the current key (e.g. key was rotated without re-encrypting existing rows)."""
    if token is None:
        return None
    try:
        return _get_fernet().decrypt(token.encode("utf-8")).decode("utf-8")
    except InvalidToken as e:
        raise ValueError(
            "Could not decrypt stored value — SECRET_ENCRYPTION_KEY may have changed, "
            "or this value was not encrypted with the current key."
        ) from e
