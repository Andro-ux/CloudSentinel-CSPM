import os

from dotenv import load_dotenv

load_dotenv()


class Settings:
    def __getattr__(self, name: str):
        env_map = {
            "CLOUD_PROVIDER": ("gcp", str),
            "DATABASE_URL": ("sqlite:///cloudsentinel.db", str),
            "JWT_SECRET_KEY": ("dev-secret-key-change-in-production", str),
            "JWT_ALGORITHM": ("HS256", str),
            "ACCESS_TOKEN_EXPIRE_MINUTES": ("60", int),
            "REFRESH_TOKEN_EXPIRE_DAYS": ("7", int),
            "BOOTSTRAP_TOKEN": (None, str),
        }
        if name in env_map:
            default, type_func = env_map[name]
            value = os.getenv(name, default)
            if value is None:
                return None
            try:
                return type_func(value)
            except (ValueError, TypeError):
                return default
        raise AttributeError(f"Settings has no attribute '{name}'")


settings = Settings()
