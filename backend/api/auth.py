import os
import hashlib
import jwt
from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from backend.database.session import get_db
from backend.database.models import User


class AuthConfigError(Exception):
    """Raised when required auth configuration is missing. This is a startup-time
    failure, not a runtime one - the app should refuse to boot rather than run with
    an insecure default."""


def _load_secret_key() -> str:
    key = os.getenv("JWT_SECRET_KEY")
    if not key:
        raise AuthConfigError(
            "JWT_SECRET_KEY is not set. There is no default - generate one with "
            "`python -c \"import secrets; print(secrets.token_urlsafe(48))\"` and set "
            "it as an environment variable before starting CloudSentinel."
        )
    if len(key) < 32:
        raise AuthConfigError(
            "JWT_SECRET_KEY is too short to be secure (minimum 32 characters). "
            "Generate one with `python -c \"import secrets; print(secrets.token_urlsafe(48))\"`."
        )
    return key


# JWT settings - fails at import time (i.e. at app startup) if misconfigured,
# rather than silently falling back to a known, hardcoded secret.
SECRET_KEY = _load_secret_key()
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
MIN_PASSWORD_LENGTH = 12

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def validate_password_strength(password: str):
    """Minimal password policy. Raises HTTPException(400) if the password is too weak.
    This isn't a substitute for proper policy enforcement (e.g. breach-list checking)
    but stops the trivially bad case of 1-8 character passwords."""
    if len(password) < MIN_PASSWORD_LENGTH:
        raise HTTPException(
            status_code=400,
            detail=f"Password must be at least {MIN_PASSWORD_LENGTH} characters long.",
        )


# --- Password Hashing Helpers using standard hashlib ---
def hash_password(password: str) -> str:
    """
    Hashes a password using PBKDF2 with a secure random salt.
    Returns: salt_hex$hash_hex
    """
    salt = os.urandom(16)
    db_hash = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt,
        100000 # iterations
    )
    return f"{salt.hex()}${db_hash.hex()}"

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies a password against the stored salt$hash representation.
    """
    try:
        salt_hex, hash_hex = hashed_password.split("$")
        salt = bytes.fromhex(salt_hex)
        db_hash = bytes.fromhex(hash_hex)
        
        new_hash = hashlib.pbkdf2_hmac(
            'sha256',
            plain_password.encode('utf-8'),
            salt,
            100000
        )
        return new_hash == db_hash
    except Exception:
        return False


# --- JWT Token Helpers ---
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
        
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    return user
