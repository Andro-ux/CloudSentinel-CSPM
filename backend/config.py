import os

from dotenv import load_dotenv

load_dotenv()


class Settings:

    CLOUD_PROVIDER = os.getenv("CLOUD_PROVIDER", "gcp")

    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        "sqlite:///cloudsentinel.db"
    )


settings = Settings()