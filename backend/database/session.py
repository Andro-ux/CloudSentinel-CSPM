import os
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, declarative_base

# Use SQLite by default, easily upgradeable to PostgreSQL
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./cloudsentinel.db")

engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
)

# Enable WAL mode for SQLite to support concurrent reading and writing
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    if DATABASE_URL.startswith("sqlite"):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA synchronous=NORMAL")
        cursor.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_setting_value(key: str, default: str = None) -> str:
    import os
    import logging
    logger = logging.getLogger("cloudsentinel.settings")

    # First priority: check if defined in environment
    env_val = os.getenv(key)
    if env_val:
        return env_val

    # Second priority: query database settings
    db = SessionLocal()
    try:
        from backend.database.models import Setting
        try:
            setting = db.query(Setting).filter(Setting.key == key).first()
        except Exception as e:
            logger.error(f"Database error fetching setting '{key}': {e}")
            return default

        if not setting or setting.value is None:
            return default

        if setting.is_encrypted:
            from backend.utils.crypto import decrypt_value, EncryptionConfigError
            try:
                return decrypt_value(setting.value)
            except (ValueError, EncryptionConfigError) as e:
                # Don't silently fall through to `default` here - that would look
                # identical to "nobody configured this setting", hiding a real
                # misconfiguration (wrong/rotated SECRET_ENCRYPTION_KEY).
                logger.error(f"Failed to decrypt setting '{key}': {e}")
                raise

        return setting.value
    finally:
        db.close()


